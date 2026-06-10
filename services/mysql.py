from services.base import run_script

SERVICE_NAME = ["mysql", "mariadb", "mysqld", "mariadbd"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server
    systemctl enable mariadb && systemctl start mariadb
elif command -v dnf > /dev/null; then
    dnf install -y mariadb-server
    systemctl enable mariadb && systemctl start mariadb
elif command -v yum > /dev/null; then
    yum install -y mariadb-server
    systemctl enable mariadb && systemctl start mariadb
else
    echo "[mysql] No supported package manager found" >&2; exit 1
fi
echo "[mysql/mariadb] Done"
"""


def install(client, password: str):
    print("  [mysql] Installing MariaDB...")
    out, err = run_script(client, password, _SCRIPT, "mysql")
    if out: print(f"  [mysql] {out.strip()}")
    if err: print(f"  [mysql] stderr: {err.strip()}")
