import mysql.connector
from mysql.connector import Error
import pandas as pd
host_name = "localhost"
username = "root"
pw = ''

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def pop_capsules_table(ratios,parameter):
    connection = create_server_connection("localhost", "root", pw)
    CapsuleDB_name = "CapsuleDB"
    create_capsule_database_query = f"CREATE DATABASE IF NOT EXISTS {CapsuleDB_name}"
    create_database(connection, create_capsule_database_query)
    
    create_user_table = """
                CREATE TABLE IF NOT EXISTS users (
                    id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(25) NOT NULL,
                    apepat VARCHAR(25) NOT NULL,
                    apemat VARCHAR(25) NOT NULL,
                    usuario VARCHAR(12) NOT NULL UNIQUE,
                    password varchar(12) NOT NULL,
                    created DATETIME NOT NULL,
                    updated DATETIME NOT NULL
                    );
                    """
    create_capsule_table = """
                CREATE TABLE IF NOT EXISTS capsules (
                    id_image INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    fechaDeMuestra DATETIME,
                    id_usuario INT,
                    segmento_molde ENUM('1', '2', '3'),
                    no_muestra INT,
                    b_tombola BOOL,
                    tanque ENUM('1','2'),
                    lote INT,
                    ratio_espesor DOUBLE(5,4),
                    parametro_calidad VARCHAR(6),
                    FOREIGN KEY (id_usuario) REFERENCES users(id_usuario)
                    );
                    """
    connection = create_db_connection(
        "localhost", "root", pw, CapsuleDB_name)  
    execute_query(connection, create_user_table)  
    execute_query(connection, create_capsule_table)

    query = f"""
            INSERT INTO capsules (ratio_espesor,parametro_calidad)
            VALUES ({ratios['ratio_average']},{parameter});
            """
    connection = create_db_connection(
        "localhost", "root", pw, CapsuleDB_name)
    execute_query(connection, query)

