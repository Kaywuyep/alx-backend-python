import aiosqlite
import asyncio

DB_PATH = "ALX_prodev.db"


async def async_fetch_users():
    """
    Asynchronously fetch all users from the 'users' table.

    Returns:
        list: A list of all user records.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()


async def async_fetch_older_users():
    """
    Asynchronously fetch users from the 'users' table where age > 40.

    Returns:
        list: A list of user records where age is greater than 40.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            return await cursor.fetchall()


async def fetch_concurrently():
    """
    Executes async_fetch_users and async_fetch_older_users concurrently
    using asyncio.gather, and prints the results.
    """
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    print("All Users:")
    for user in all_users:
        print(user)

    print("\nUsers Older Than 40:")
    for user in older_users:
        print(user)


# Entry point
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
