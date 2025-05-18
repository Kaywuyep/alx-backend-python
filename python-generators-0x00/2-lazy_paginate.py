#!/usr/bin/python3
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches a page of user data from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    A generator function that lazily loads pages of user data.
    It fetches the next page only when needed, starting at an offset of 0.
    """
    offset: int = 0
    while True:
        rows = paginate_users(page_size, offset)
        # print(rows)

        if not rows:
            break
        
        # yield results
        yield rows
        
        # increment offset
        offset += page_size
