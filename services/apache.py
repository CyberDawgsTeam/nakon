from services.base import run_script

SERVICE_NAME = ["apache", "apache2", "httpd"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
    systemctl enable apache2 && systemctl start apache2
elif command -v dnf > /dev/null; then
    dnf install -y httpd
    systemctl enable httpd && systemctl start httpd
elif command -v yum > /dev/null; then
    yum install -y httpd
    systemctl enable httpd && systemctl start httpd
else
    echo "[apache] No supported package manager found" >&2; exit 1
fi
echo "[apache] Done"
"""


def install(client, password: str):
    print("  [apache] Installing Apache...")
    out, err = run_script(client, password, _SCRIPT, "apache")
    if out: print(f"  [apache] {out.strip()}")
    if err: print(f"  [apache] stderr: {err.strip()}")
