#!/usr/bin/env python3
""" a simple module"""
from typing import Tuple, Union


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """ a tuple module """
    return (k, float(v**2))
