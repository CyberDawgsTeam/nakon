from services.base import run_script

SERVICE_NAME = ["dovecot", "imap", "pop3"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y dovecot-core dovecot-imapd dovecot-pop3d
elif command -v dnf > /dev/null; then
    dnf install -y dovecot
elif command -v yum > /dev/null; then
    yum install -y dovecot
else
    echo "[dovecot] No supported package manager found" >&2; exit 1
fi
systemctl enable dovecot && systemctl start dovecot
echo "[dovecot] Done"
"""


def install(client, password: str):
    print("  [dovecot] Installing Dovecot...")
    out, err = run_script(client, password, _SCRIPT, "dovecot")
    if out: print(f"  [dovecot] {out.strip()}")
    if err: print(f"  [dovecot] stderr: {err.strip()}")
