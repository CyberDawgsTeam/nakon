import mysql.connector
import json
import paramiko
import os
from dotenv import load_dotenv
import dependencies

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

db_config = {
    "host":     os.getenv("host"),
    "user":     os.getenv("user"),
    "password": os.getenv("password"),
    "database": os.getenv("database"),
}


def sudo_pass(stdin, password: str):
    stdin.write(password + "\n")
    stdin.flush()


mydb = mysql.connector.connect(**db_config)
cursor = mydb.cursor()

# ── 1. Install all dependencies across all machines before any misconfigs run ─
dependencies.run(config, db_config)

# ── 2. Deploy misconfigurations ───────────────────────────────────────────────
for machine in config["machines"]:
    print(f"\n[deploy] ── Machine: {machine['ip']} ──────────────────────────────")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=machine["ip"],
        username=machine["user"],
        password=machine["password"],
    )

    for vuln in machine["vulns"]:
        cursor.execute(
            """
            SELECT m.script, m.run_as
            FROM misconfigs m
            JOIN vulnerabilities v ON m.vuln_id = v.id
            WHERE m.id = %s
            """,
            (vuln["id"],),
        )
        item = cursor.fetchone()

        cmd   = item[0]
        runAs = item[1]

        # Write the script to /tmp on the remote host
        stdin, stdout, stderr = client.exec_command(
            f"cat << 'DEPLOY_EOF' > /tmp/cmd.sh\n{cmd}\nDEPLOY_EOF"
        )
        stdout.read()

        stdin, stdout, stderr = client.exec_command("chmod +x /tmp/cmd.sh")
        stdout.read()

        if runAs == "root":
            stdin, stdout, stderr = client.exec_command("sudo -S sh /tmp/cmd.sh")
            sudo_pass(stdin, machine["password"])
        else:
            stdin, stdout, stderr = client.exec_command("sh /tmp/cmd.sh")

        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(f"[deploy] {out.strip()}")
        if err: print(f"[deploy] stderr: {err.strip()}")

    client.close()

cursor.close()
mydb.close()
