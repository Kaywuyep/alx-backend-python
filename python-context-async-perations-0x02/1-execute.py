""" Reusable Query Context Manager"""
import sqlite3


class ExecuteQuery:
    """
    A context manager to execute a database query
    and manage the connection lifecycle.

    Attributes:
        db_path (str): Path to the SQLite database file.
        query (str): The SQL query to execute.
        params (tuple): Parameters to use in the SQL query.
    """
    def __init__(self, db_path, query, params=()):
        """
        Initializes the context manager with database path,
        query, and parameters.

        Args:
            db_path (str): Path to the SQLite database file.
            query (str): SQL query to execute.
            params (tuple): Optional query parameters (default is empty tuple).
        """
        self.db_path = db_path
        self.query = query
        self.params = params
        self.connection = None
        self.cursor = None
        self.result = None

    def __enter__(self):
        """
        Establishes a database connection, executes the query,
        and returns the result.

        Returns:
            list: A list of rows returned by the query.
        """
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        self.result = self.cursor.fetchall()
        return self.result

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the cursor and connection. Handles exceptions if any occur.

        Args:
            exc_type (type): Exception type (if any).
            exc_value (Exception): Exception value (if any).
            traceback (TracebackType): Traceback object (if any).
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        # Returning False will propagate the exception, if any
        return False


if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    db_path = "example.db"

    with ExecuteQuery(db_path, query, params) as result:
        for row in result:
            print(row)
