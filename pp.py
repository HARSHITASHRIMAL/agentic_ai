#this is a  file to know about the tables in the database
# This script lists all tables in the northwind.db SQLite database 
import sqlite3

conn = sqlite3.connect("northwind.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
conn.close()
