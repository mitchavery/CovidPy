import mysql.connector


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="Saxdude135",
  database="covid"
)

mycursor = mydb.cursor()