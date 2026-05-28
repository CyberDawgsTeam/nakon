import mysql.connector
import json
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

with open("config.json") as f:
    config = json.load(f)

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
    print(machine["ip"])

#client = paramiko.SSHClient()
#client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#client.connect(hostname='://server.com', username='your_user', password='your_password')
#stdin, stdout, stderr = client.exec_command('ls -l')
#print(stdout.read().decode())
#client.close()
