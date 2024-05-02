#!/usr/bin/env python3
"""a simple module"""
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """ a multiplier functtion"""
    def multiplier_function(x: float) -> float:
        return x * multiplier
    return multiplier_function
