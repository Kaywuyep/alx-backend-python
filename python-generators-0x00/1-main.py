# """ generator that streams rows from an SQL database"""

# #!/usr/bin/python3
# from itertools import islice
# stream_users = __import__('0-stream_users')

# # iterate over the generator function and print only the first 6 rows

# for user in islice(stream_users(), 6):
#     print(user)

#!/usr/bin/python3
from itertools import islice
from importlib import import_module

# Import the module and get the function
module = import_module('0-stream_users')
stream_users = module.stream_users

# iterate over the generator function and print only the first 6 rows
for user in islice(stream_users(), 6):
    print(user)
