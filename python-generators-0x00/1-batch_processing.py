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
    """
    Generator function that fetches rows in batches from the user_data table.

    Args:
        batch_size (int): Number of users to fetch in each batch

    Yields:
        list: A batch of user records as dictionaries
    """
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection:
            with connection.cursor() as cursor:
                # Get total count to know how many batches we need
                cursor.execute("SELECT COUNT(*) as count FROM user_data")
                total_users = cursor.fetchone()['count']

                # Calculate number of batches
                offset = 0

                # Fetch data in batches
                while offset < total_users:
                    cursor.execute(
                        "SELECT * FROM user_data LIMIT %s OFFSET %s",
                        (batch_size, offset)
                    )
                    batch = cursor.fetchall()

                    if not batch:
                        break

                    yield batch
                    offset += batch_size

    except Exception as e:
        print(f"Error fetching data: {e}")


def batch_processing(batch_size):
    """
    Processes batches of users to filter out those over the age of 25.

    Args:
        batch_size (int): The size of each batch to process
    """
    # Using stream_users_in_batches to get batches
    for batch in stream_users_in_batches(batch_size):
        # Process each batch - filter users over age 25
        filtered_users = [
            user for user in batch if float(user['age']) > 25
        ]

        # Print processed results
        if filtered_users:
            print(f"Found {len(filtered_users)} users over 25 years old in this batch:")
            for user in filtered_users:
                print(f"User: {user['name']}, Age: {user['age']}, Email: {user['email']}")
            print("-" * 50)
        else:
            print("No users over 25 years old found in this batch.")
            print("-" * 50)
