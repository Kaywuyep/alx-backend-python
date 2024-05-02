#!/usr/bin/env python3
"""a simple module"""
from typing import Iterable, Sequence, Tuple, List


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """returns a list of Tuples"""
    return [(i, len(i)) for i in lst]
