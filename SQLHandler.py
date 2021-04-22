import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db = None):
    connection = None
    try:
        if (db == None):
            connection = mysql.connector.connect(
                host = host_name,
                user = user_name,
                passwd = user_password)
        else:    
            connection = mysql.connector.connect(
                host = host_name,
                user = user_name,
                passwd = user_password,
                database = db)
        #     port = 3306,
        #     auth_plugin = 'mysql_native_password'
        # #)
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
        print("This database doesn't exist")

    return connection


def execute_query(connection, query, msg, creation_query):
    my_cursor = connection.cursor()
    try:
        my_cursor.execute(query)
        # if not creation_query:
        #     my_cursor.commit()
        print(msg)
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


def create_database(connection, query):
    msg = "Database created successfully"
    execute_query(connection, query, msg, creation_query = True)

def select_database(connection, query):
    msg = "All dbs created are displayed"
    # msg = "Database is selected succesfully"
    execute_query(connection, query, msg, creation_query = False)
    
def delete_database(connection, query):
    msg = "Selected database deleted successfully"
    execute_query(connection, query, msg, creation_query = False)

def create_table(connection, query):
    msg = "Table added successfully"
    execute_query(connection, query, msg, creation_query = False)

def add_records(connection, query):
    msg = "Records added successfully"
    execute_query(connection, query, msg, creation_query = False)
    
def update_records(connection, query):
    msg = "Record updated successfully"
    execute_query(connection, query, msg, False)

def erase_table(connection, query):
    msg = "Table dropped successfully"
    execute_query(connection, query, msg, creation_query = False)

def delete_records(connection, query):
    msg = "Record deleted successfully"
    execute_query(connection, query, msg, False)