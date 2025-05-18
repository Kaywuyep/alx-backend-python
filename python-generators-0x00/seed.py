#!/usr/bin/env python3
"""
Script to set up MySQL database and populate it with sample data.
"""
import os
import csv
import pymysql
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )
        print("Successfully connected to MySQL server")
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL server: {e}")
        return None


def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database 'ALX_prodev' created or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
            )
        print("Successfully connected to ALX_prodev database")
        return connection
    except Exception as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX (user_id)
        )
        """)
        print("Table 'user_data' created or already exists")
    except Exception as e:
        print(f"Error creating table: {e}")


def insert_data(connection, data):
    """
    Inserts data in the database if it does not exist.
    'data' can be either a dictionary or a path to a CSV file.
    """
    try:
        # Check if data is a string (filepath)
        if isinstance(data, str):
            load_csv_data(connection, data)
            return

        # If data is a dictionary, proceed with individual insert
        cursor = connection.cursor()

        # First check if the user_id already exists
        query = "SELECT user_id FROM user_data WHERE user_id = %s"
        cursor.execute(query, (data['user_id'],))
        result = cursor.fetchone()

        if result is None:  # User does not exist, insert the data
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            values = (data['user_id'], data['name'], data['email'], data['age'])
            cursor.execute(insert_query, values)
            connection.commit()
            print(f"Data for {data['name']} inserted successfully")
        else:
            print(f"User with ID {data['user_id']} already exists. Skipping.")
    except Exception as e:
        print(f"Error inserting data: {e}")


def load_csv_data(connection, file_path):
    """Load data from CSV file and populate the database"""
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Generate UUID if not present
                if 'user_id' not in row or not row['user_id']:
                    row['user_id'] = str(uuid.uuid4())

                # Insert the data
                insert_row(connection, row)

    except Exception as e:
        print(f"Error loading CSV data: {e}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")


def insert_row(connection, data):
    """Insert a single row of data"""
    try:
        cursor = connection.cursor()

        # First check if the user_id already exists
        query = "SELECT user_id FROM user_data WHERE user_id = %s"
        cursor.execute(query, (data['user_id'],))
        result = cursor.fetchone()

        if result is None:  # User does not exist, insert the data
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
            """
            values = (data['user_id'], data['name'], data['email'], data['age'])
            cursor.execute(insert_query, values)
            connection.commit()
            print(f"Data for {data['name']} inserted successfully")
        else:
            print(f"User with ID {data['user_id']} already exists. Skipping.")
    except Exception as e:
        print(f"Error inserting data: {e}")


def stream_rows_generator(connection=None, query="SELECT * FROM user_data"):
    """Generator function to stream rows from the database one by one"""
    # If no connection is provided, create a new one
    should_close_connection = False
    if connection is None:
        connection = connect_to_prodev()
        should_close_connection = True

    if connection is None:
        return

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)

        # Yield rows one by one
        for row in cursor:
            yield row

    except Exception as e:
        print(f"Error streaming data: {e}")
    finally:
        if should_close_connection and connection.is_connected():
            cursor.close()
            connection.close()
