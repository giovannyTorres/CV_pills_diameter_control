"""Database utilities for capsule measurements."""
import mysql.connector
from mysql.connector import Error


class CapsuleDatabase:
    """Handle database operations for capsule measurements."""

    def __init__(self, host: str, user: str, password: str, db_name: str = "CapsuleDB") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def create_server_connection(self):
        """Connect to the MySQL server without specifying a database."""
        try:
            connection = mysql.connector.connect(
                host=self.host, user=self.user, passwd=self.password
            )
            return connection
        except Error as err:
            print(f"Error: '{err}'")
            return None

    def create_database(self, connection):
        """Create the database if it does not exist."""
        query = f"CREATE DATABASE IF NOT EXISTS {self.db_name}"
        self.execute_query(connection, query)

    def create_db_connection(self):
        """Connect to the specific database."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                database=self.db_name,
            )
            return connection
        except Error as err:
            print(f"Error: '{err}'")
            return None

    @staticmethod
    def execute_query(connection, query):
        """Execute a single query using the provided connection."""
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
        except Error as err:
            print(f"Error: '{err}'")

    def setup_database(self):
        """Ensure database and tables exist."""
        server_conn = self.create_server_connection()
        if server_conn:
            self.create_database(server_conn)
        db_conn = self.create_db_connection()
        if db_conn:
            user_table = (
                """CREATE TABLE IF NOT EXISTS users (
                id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(25) NOT NULL,
                apepat VARCHAR(25) NOT NULL,
                apemat VARCHAR(25) NOT NULL,
                usuario VARCHAR(12) NOT NULL UNIQUE,
                password VARCHAR(12) NOT NULL,
                created DATETIME NOT NULL,
                updated DATETIME NOT NULL
            );"""
            )
            capsule_table = (
                """CREATE TABLE IF NOT EXISTS capsules (
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
            );"""
            )
            self.execute_query(db_conn, user_table)
            self.execute_query(db_conn, capsule_table)

    def insert_capsule(self, ratio: float, parameter: bool):
        """Insert a capsule measurement record."""
        connection = self.create_db_connection()
        if connection:
            query = (
                "INSERT INTO capsules (ratio_espesor, parametro_calidad) "
                f"VALUES ({ratio}, {int(parameter)});"
            )
            self.execute_query(connection, query)
