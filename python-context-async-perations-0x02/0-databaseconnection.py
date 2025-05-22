import sqlite3


class DatabaseConnection:
    """
    A context manager class for handling SQLite database connections.

    This class simplifies the process of opening and closing
    database connections.
    It ensures that connections are properly committed and
    closed when exiting the context, and rolled back in case of an exception.

    Attributes:
        db_name (str): The name of the SQLite database file.
        connection (sqlite3.Connection): The database connection object.
        cursor (sqlite3.Cursor): The cursor object used to execute queries.
    """

    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection context manager.

        Args:
            db_name (str): The name (or path) of the SQLite database file.
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        Open the database connection and return a cursor object.

        Returns:
            sqlite3.Cursor: A cursor object for executing SQL queries.
        """
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the cursor and connection when exiting the context.

        If an exception occurred, the transaction is rolled back.
        Otherwise, the transaction is committed.

        Args:
            exc_type (type): The exception type, if any.
            exc_value (Exception): The exception instance, if any.
            traceback (traceback): The traceback object, if any.
        """
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.cursor.close()
            self.connection.close()


if __name__ == "__main__":
    db_name = "ALX_prodev.db"

    # Setup example table and data (only for demonstration)
    with DatabaseConnection(db_name) as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
        cursor.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))

    # Use the context manager to fetch data
    with DatabaseConnection(db_name) as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print("User records:")
        for row in results:
            print(row)