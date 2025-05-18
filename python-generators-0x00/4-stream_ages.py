#!/usr/bin/python3
users = __import__("0-stream_users").stream_users


def stream_user_ages():
    """
    Generator that yields ages of users one by one.

    Yields:
        int: Age of a user.
    """
    for user in users():
        yield user["age"]


def calculate_average_age():
    """
    Calculate the average age of users by consuming the stream_user_ages generator.

    Returns:
        float: The average age of all users. Returns 0 if no users.
    """
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    if count == 0:
        return 0
    return total_age / count
