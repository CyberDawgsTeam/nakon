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
cursor.execute("SELECT * FROM misconfigs;")

myresult = cursor.fetchall()

for x in myresult:
    print(x)

print(config['machines'][1])

for machine in config['machines']:
    client = paramiko.SSHClient()
    #fixes unknown host key stuff
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #use creds from config
    client.connect(hostname=machine["ip"], username=machine["user"], password=machine["password"])
    stdin, stdout, stderr = client.exec_command('sudo -S id')
    sudo_pass()

    print(stdout.read().decode())
    client.close()
