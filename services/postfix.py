from services.base import run_script

SERVICE_NAME = ["postfix", "smtp", "sendmail", "mail"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y postfix
elif command -v dnf > /dev/null; then
    dnf install -y postfix
elif command -v yum > /dev/null; then
    yum install -y postfix
else
    echo "[postfix] No supported package manager found" >&2; exit 1
fi
systemctl enable postfix && systemctl start postfix
echo "[postfix] Done"
"""


def install(client, password: str):
    print("  [postfix] Installing Postfix...")
    out, err = run_script(client, password, _SCRIPT, "postfix")
    if out: print(f"  [postfix] {out.strip()}")
    if err: print(f"  [postfix] stderr: {err.strip()}")
