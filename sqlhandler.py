import mysql.connector
from mysql.connector import Error

# Set of functions that perform MySQL operations in a lower layer than dboperations. They make all the steps necessary
# to connect to a MySQL database and perform the operations.

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
        # print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    my_cursor = connection.cursor()
    try:
        my_cursor.execute(query)
        my_cursor.close()
    except Error as e:
        print("The error '{}' occurred".format(e))

def execute_insertion_query(connection, query, content):
    try:
        cursor = connection.cursor(buffered = True)
        cursor.execute(query, content)
        connection.commit()
        cursor.close()
    except Error as e:
        print("Failed to insert data {}".format(e))

def execute_deletion_query(connection, query, content):
    try:
        cursor = connection.cursor()
        cursor.executemany(query, content)
        connection.commit()
        cursor.close()
    except Error as e:
        print("Failed to delete data {}".format(e))

def execute_read_query(connection, query, content = None):
    cursor = connection.cursor()
    result = None
    try:
        if content == None:
            cursor.execute(query)
        else:
            cursor.execute(query, content)
        result = cursor.fetchall()
    except Error as e:
        print("The error '{}' occurred".format(e))
    return result