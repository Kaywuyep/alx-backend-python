"""Using decorators to cache Database Queries"""
import time
import sqlite3
import functools

query_cache = {}


def with_db_connection(func):
    """
    Decorator that manages a SQLite database connection.

    It opens a connection to 'users.db', passes it to the decorated function as the
    first argument, and ensures the connection is closed afterward, regardless of success or error.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper


def cache_query(func):
    """
    Decorator that caches the result of a database query based on the SQL query string.
    
    If the query string has been seen before, returns the cached result instead of executing it again.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Determine the query string from args or kwargs
        query = kwargs.get('query') or (args[0] if args else None)
        if query in query_cache:
            print("Using cached result for query.")
            return query_cache[query]

        print("Executing and caching query.")
        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")


# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
