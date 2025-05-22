import sqlite3
import functools

from datetime import datetime


# Decorator to log SQL queries
def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    Assumes the first argument of the decorated function
    is a 'query' parameter.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query') or (args[0] if args else '')
        print(f"[{datetime.now()}] Executing SQL query: {query}")
        return func(*args, **kwargs)
    return wrapper


@log_queries
def fetch_all_users(query):
    """
    Fetch all users from the database.
    Args:
        query (str): SQL query to execute.
        Returns:
        list: List of tuples containing user data.
        """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
