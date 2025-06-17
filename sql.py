import sqlite3

def import_sql_file(db_path, sql_file_path):
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sql_script)  # Executes multiple SQL commands at once
    conn.commit()
    conn.close()
    print(f"Imported {sql_file_path} successfully into {db_path}")

# Example usage:
import_sql_file("northwind.db", "create.sql")

