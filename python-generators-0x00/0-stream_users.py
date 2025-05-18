#!/usr/bin/python3
"""Generator function to stream rows from the user_data table one by one."""
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def stream_users():
    """
    Generator function that fetches rows one by one from the user_data table.
    Uses the yield keyword to return each row individually.
    Contains no more than 1 loop.
    """
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            cursorclass=pymysql.cursors.DictCursor  # Return results as dictionaries
        )

        with connection:
            # Create a cursor and execute query
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM user_data")
    
                # Use a single loop to yield rows one by one
                for row in cursor:
                    yield row

    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
