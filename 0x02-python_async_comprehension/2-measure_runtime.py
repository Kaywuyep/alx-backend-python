#!/usr/bin/env python3
"""an async module"""


from asyncio import gather
from time import time

async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """ Measure the runtime of async_comprehension executed 4 times in
        parallel. """
    firstTime = time()
    await gather(async_comprehension(), async_comprehension(),
                 async_comprehension(), async_comprehension())
    nextTime = time()

    return nextTime - firstTime
