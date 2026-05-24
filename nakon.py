import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

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
