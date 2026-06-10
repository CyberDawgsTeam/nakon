import mysql.connector
import json
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

#call this after every sudo command to pass the password
def sudo_pass():
    #pass password for sudo
    stdin.write(machine["password"] + '\n')
    stdin.flush()


mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database")
)
cursor = mydb.cursor()

#main loop
for machine in config['machines']:
    client = paramiko.SSHClient()
    #fixes unknown host key stuff
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #use creds from config
    client.connect(hostname=machine["ip"], username=machine["user"], password=machine["password"])

    #secondary loop for vulns
    for vuln in machine["vulns"]:
        cursor.execute("SELECT * FROM misconfigs WHERE id=" + str(vuln["id"]))
        item = cursor.fetchall()

        #0=id, 1=vuln_id, 2=type, 3=script, 4=runas
        runAs = item[0][4]
        cmd = item[0][3]
        stdin, stdout, stderr = client.exec_command("cat << EOF > /tmp/cmd.sh\n" + cmd + "\nEOF")
        stdin, stdout, stderr = client.exec_command("chmod +x /tmp/cmd.sh")
        if runAs == "root":
            stdin, stdout, stderr = client.exec_command("sudo -S sh /tmp/cmd.sh")
            sudo_pass()
            print(stdout.read().decode())
            print(stderr.read().decode())
        else:
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())

    print(stdout.read().decode())
    client.close()
