from services.base import run_script

SERVICE_NAME = ["vsftpd", "ftp"]

_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y vsftpd
elif command -v dnf > /dev/null; then
    dnf install -y vsftpd
elif command -v yum > /dev/null; then
    yum install -y vsftpd
else
    echo "[vsftpd] No supported package manager found" >&2; exit 1
fi
systemctl enable vsftpd && systemctl start vsftpd
echo "[vsftpd] Done"
"""


def install(client, password: str):
    print("  [vsftpd] Installing vsftpd...")
    out, err = run_script(client, password, _SCRIPT, "vsftpd")
    if out: print(f"  [vsftpd] {out.strip()}")
    if err: print(f"  [vsftpd] stderr: {err.strip()}")
