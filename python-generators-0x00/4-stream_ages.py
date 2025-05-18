#!/usr/bin/python3
import pymysql.cursors # Import the cursors module for DictCursor

seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a page of user data from the database.
    (This function is reused from the previous problem, assuming it's available)
    """

    connection = seed.connect_to_prodev()
    cursor = connection.cursor(cursorclass=pymysql.cursors.DictCursor)
    cursor.execute(f"SELECT age FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def stream_user_ages(page_size=1000):
    """
    A generator function that yields user ages one by one from the database.
    It uses pagination to avoid loading the entire dataset into memory.
    """
    offset = 0
    while True:
        # Fetch a page of users (containing only 'age' for efficiency)
        page = paginate_users(page_size, offset)
        if not page:
            break  # No more data

        # Yield each user's age from the current page
        for user_data in page:
            yield user_data['age']

        offset += page_size


def calculate_average_age():
    """
    Calculates the average age of users by streaming ages,
    without loading the entire dataset into memory.
    """
    total_age = 0
    user_count = 0

    # Loop 1: Iterates through the ages yielded by the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1

    if user_count == 0:
        return 0  # Avoid division by zero if no users are found
    else:
        return total_age / user_count
