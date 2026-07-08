import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="preschool",
    password="excel",
    database="flaskapp"
)

cursor = db.cursor(dictionary=True)