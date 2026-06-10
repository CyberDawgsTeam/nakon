"""
Dependency installer for the misconfiguration deployer.

For each machine in config:
  1. Collects all misconfig IDs assigned to that machine
  2. Queries the DB for unique dependencies across those vulns
  3. For each dep, runs a service-specific installer if one is registered,
     otherwise falls back to the system package manager

Called from deploy.py before the misconfiguration deploy loop runs.
"""

import json
import mysql.connector
import paramiko
from services import REGISTRY
from services.base import install_package


def _get_deps_for_machine(cursor, misconfig_ids: list) -> list:
    """
    Return a deduplicated list of all dependency strings for the given
    misconfig IDs by joining misconfigs -> vulnerabilities.
    """
    if not misconfig_ids:
        return []

    placeholders = ", ".join(["%s"] * len(misconfig_ids))
    cursor.execute(
        f"""
        SELECT DISTINCT v.dependencies
        FROM misconfigs m
        JOIN vulnerabilities v ON m.vuln_id = v.id
        WHERE m.id IN ({placeholders})
        """,
        tuple(misconfig_ids),
    )

    deps: set = set()
    for (deps_raw,) in cursor.fetchall():
        if not deps_raw:
            continue
        # mysql.connector may already deserialize JSON columns into a list
        if isinstance(deps_raw, list):
            parsed = deps_raw
        else:
            parsed = json.loads(deps_raw)
        deps.update(parsed)

    return list(deps)


def _install_on_machine(client, password: str, deps: list):
    """
    Iterate over deps; route to a service installer when available,
    otherwise fall back to package manager install.
    """
    for dep in deps:
        dep_key = dep.lower()
        if dep_key in REGISTRY:
            print(f"  [deps] '{dep}' matched service installer")
            REGISTRY[dep_key](client, password)
        else:
            print(f"  [deps] '{dep}' not in registry — installing via package manager")
            install_package(client, password, dep)


def run(config: dict, db_config: dict):
    """
    Entry point called by deploy.py.
    Opens its own short-lived DB connection so deploy.py keeps its own cursor.
    """
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    for machine in config["machines"]:
        ip = machine["ip"]
        print(f"\n[deps] ── Machine: {ip} ──────────────────────────────")

        misconfig_ids = [v["id"] for v in machine.get("vulns", [])]
        if not misconfig_ids:
            print("[deps] No vulns configured, skipping.")
            continue

        deps = _get_deps_for_machine(cursor, misconfig_ids)
        if not deps:
            print("[deps] No dependencies found.")
            continue

        print(f"[deps] Installing: {deps}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=ip,
            username=machine["user"],
            password=machine["password"],
        )
        try:
            _install_on_machine(client, machine["password"], deps)
        finally:
            client.close()

    cursor.close()
    db.close()
    print("\n[deps] All machines done.")
