import sqlite3
import functools


# decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    Assumes the first argument of the decorated function is a
    'query' parameter.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from arguments
        query = None

        # Check if query is passed as keyword argument
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is the first positional argument
        elif args and len(args) > 0:
            query = args[0]

        # Log the query if found
        if query:
            print(f"Executing SQL Query: {query}")
        else:
            print("No query found to log")

        # Execute the original function
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
