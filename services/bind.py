from services.base import run_script

SERVICE_NAME = ["bind", "bind9", "named", "dns"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y bind9 bind9utils bind9-doc
    systemctl enable bind9  && systemctl start bind9
elif command -v dnf > /dev/null; then
    dnf install -y bind bind-utils
    systemctl enable named && systemctl start named
elif command -v yum > /dev/null; then
    yum install -y bind bind-utils
    systemctl enable named && systemctl start named
else
    echo "[bind] No supported package manager found" >&2; exit 1
fi
echo "[bind] Done"
"""


def install(client, password: str):
    print("  [bind] Installing BIND9...")
    out, err = run_script(client, password, _SCRIPT, "bind")
    if out: print(f"  [bind] {out.strip()}")
    if err: print(f"  [bind] stderr: {err.strip()}")
