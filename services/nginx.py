from services.base import run_script

SERVICE_NAME = ["nginx"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
elif command -v dnf > /dev/null; then
    dnf install -y nginx
elif command -v yum > /dev/null; then
    yum install -y epel-release
    yum install -y nginx
else
    echo "[nginx] No supported package manager found" >&2; exit 1
fi
systemctl enable nginx && systemctl start nginx
echo "[nginx] Done"
"""


def install(client, password: str):
    print("  [nginx] Installing Nginx...")
    out, err = run_script(client, password, _SCRIPT, "nginx")
    if out: print(f"  [nginx] {out.strip()}")
    if err: print(f"  [nginx] stderr: {err.strip()}")
