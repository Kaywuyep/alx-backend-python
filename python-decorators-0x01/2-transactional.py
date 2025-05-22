"""Transaction Management Decorator"""
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


def transactional(func):
    """
    Decorator that wraps a database operation inside a transaction.

    It commits the transaction if the function executes successfully,
    otherwise it rolls back in case of an exception.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Update a user's email in the database."""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
