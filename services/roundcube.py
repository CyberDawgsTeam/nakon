from services.base import run_script

SERVICE_NAME = ["roundcube", "roundcubemail"]

# Roundcube depends on a web server + PHP + a database.
# This script installs Apache + MariaDB + PHP alongside Roundcube if not present.
_SCRIPT = """#!/bin/bash
set -e
if command -v apt-get > /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y \\
        apache2 mariadb-server php php-mysql php-xml php-mbstring php-intl \\
        php-net-smtp php-net-socket roundcube roundcube-mysql roundcube-plugins
    a2enconf roundcube 2>/dev/null || true
    systemctl enable apache2  && systemctl restart apache2
    systemctl enable mariadb  && systemctl start  mariadb
elif command -v dnf > /dev/null; then
    dnf install -y epel-release
    dnf install -y httpd mariadb-server php php-mysqlnd php-xml php-mbstring roundcubemail
    systemctl enable httpd   && systemctl start httpd
    systemctl enable mariadb && systemctl start mariadb
elif command -v yum > /dev/null; then
    yum install -y epel-release
    yum install -y httpd mariadb-server php php-mysql php-xml php-mbstring roundcubemail
    systemctl enable httpd   && systemctl start httpd
    systemctl enable mariadb && systemctl start mariadb
else
    echo "[roundcube] No supported package manager found" >&2; exit 1
fi
echo "[roundcube] Done"
"""


def install(client, password: str):
    print("  [roundcube] Installing Roundcube (+ Apache, MariaDB, PHP)...")
    out, err = run_script(client, password, _SCRIPT, "roundcube")
    if out: print(f"  [roundcube] {out.strip()}")
    if err: print(f"  [roundcube] stderr: {err.strip()}")
