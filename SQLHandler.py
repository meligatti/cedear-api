import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db = None):
    connection = None
    try:
        if db == None:
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


def execute_query(connection, query, msg, insert_query):
    my_cursor = connection.cursor()
    try:
        #print(query)
        my_cursor.execute(query)
        #my_cursor.execute(query)
        if insert_query:
            connection.commit()
            my_cursor.close()
         #print(msg)
    except Error as e:
        # print("The error '{e}' occurred".format(e))
        print("Failed to create database {}".format(e))

def execute_insertion_query(connection, query, content):
    try:
        cursor = connection.cursor(buffered = True)
        cursor.execute(query, content)
        connection.commit()
        cursor.close()
    except Error as e:
        print("Failed to insert data {}".format(e))

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def check_table_height(connection, table_name):
    try:
        cursor = connection.cursor(buffered = True)
        select_table_query = """SELECT * FROM """ + table_name
        cursor.execute(select_table_query)
        table_height = cursor.rowcount
        if table_height == None:
            table_height = 0
    except Error as e:
        print("Table height couldn't be checked: {}".format(e))
        table_height = 0
    finally:
        return table_height




def create_database(connection, query):
    msg = "Database created successfully"
    execute_query(connection, query, msg, insert_query = False)

def select_database(connection, query):
    msg = "All dbs created are displayed"
    # msg = "Database is selected succesfully"
    execute_query(connection, query, msg, insert_query = False)
    
def delete_database(connection, query):
    msg = "Selected database deleted successfully"
    execute_query(connection, query, msg, insert_query = False)

def create_table(connection, query):
    msg = "Table added successfully"
    execute_query(connection, query, msg, insert_query = False)

def add_records(connection, query):
    msg = "Records added successfully"
    execute_query(connection, query, msg, insert_query = True)
    
def update_records(connection, query):
    msg = "Record updated successfully"
    execute_query(connection, query, msg, False)

def erase_table(connection, query):
    msg = "Table dropped successfully"
    execute_query(connection, query, msg, insert_query = False)

def delete_records(connection, query):
    msg = "Record deleted successfully"
    execute_query(connection, query, msg, False)