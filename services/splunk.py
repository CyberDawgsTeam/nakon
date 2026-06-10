from services.base import run_script

SERVICE_NAME = ["splunk", "splunkd"]

# ── Update these to the version used in your exercise environment ──────────────
_DEB_URL = "https://download.splunk.com/products/splunk/releases/10.4.0/linux/splunk-10.4.0-f798d4d49089-linux-amd64.deb"
_RPM_URL = "https://download.splunk.com/products/splunk/releases/10.4.0/linux/splunk-10.4.0-f798d4d49089.x86_64.rpm"
_INSTALL_DIR = "/opt/splunk"
_ADMIN_PASS = "changeme123!"   # Splunk requires ≥8 chars with mixed case + digit
# ──────────────────────────────────────────────────────────────────────────────

_SCRIPT = f"""#!/bin/bash
set -e
SPLUNK="{_INSTALL_DIR}/bin/splunk"

if [ -f "$SPLUNK" ]; then
    echo "[splunk] Already installed — starting service"
    $SPLUNK start --accept-license --answer-yes --no-prompt || true
    exit 0
fi

if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget
    wget -q -O /tmp/splunk.deb "{_DEB_URL}"
    dpkg -i /tmp/splunk.deb
elif command -v dnf > /dev/null; then
    dnf install -y wget
    wget -q -O /tmp/splunk.rpm "{_RPM_URL}"
    rpm -ivh /tmp/splunk.rpm
elif command -v yum > /dev/null; then
    yum install -y wget
    wget -q -O /tmp/splunk.rpm "{_RPM_URL}"
    rpm -ivh /tmp/splunk.rpm
else
    echo "[splunk] No supported package manager found" >&2; exit 1
fi

# First-time setup: set admin password and accept license
$SPLUNK start --accept-license --answer-yes --no-prompt \\
    --seed-passwd "{_ADMIN_PASS}"
$SPLUNK enable boot-start -systemd-managed 1 || $SPLUNK enable boot-start
echo "[splunk] Done"
"""


def install(client, password: str):
    print("  [splunk] Installing Splunk Enterprise...")
    out, err = run_script(client, password, _SCRIPT, "splunk")
    if out: print(f"  [splunk] {out.strip()}")
    if err: print(f"  [splunk] stderr: {err.strip()}")
