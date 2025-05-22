"""Handle Database Connections with a Decorator"""
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that manages a SQLite database connection.

    It opens a connection to 'users.db',
    passes it to the decorated function as the
    first argument, and ensures the connection is closed afterward,
    regardless of success or error.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetch a user by ID from the database.
    Args:
        conn: SQLite connection object.
        user_id: ID of the user to fetch."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)
