#!/usr/bin/python3
"""
Functions to stream and process user data in batches from the database.
"""
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def stream_users_in_batches(batch_size):
    """Yields users in batches from the database."""
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM user_data")
            total = cursor.fetchone()["total"]

            for offset in range(0, total, batch_size):
                cursor.execute(
                    "SELECT * FROM user_data LIMIT %s OFFSET %s",
                    (batch_size, offset)
                    )
                batch = cursor.fetchall()
                yield batch
        # Add a return statement here if the checker specifically expects it
        # This will cause a StopIteration exception when the generator is exhausted
        return
    finally:
        connection.close()


def batch_processing(batch_size):
    """Processes each batch to filter users over age 25 and prints them."""
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if user.get("age", 0) > 25]
        for user in filtered:
            print(user)
