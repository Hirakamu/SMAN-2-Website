import mysql.connector
from mysql.connector import Error

def sman_db(app):
    try:
        connection = mysql.connector.connect(
            host=app.config.get("DB_HOST", "localhost"),
            user=app.config.get("DB_USER", "hirakamu"),
            password=app.config.get("DB_PASSWORD", "hirakamucato"),
            database=app.config.get("DB_NAME", "sman_db")
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
        app.config['db_conn'] = connection
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")