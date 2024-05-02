#!/usr/bin/env python3
""" a simple module"""
from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[float, int]]) -> float:
    """ a mixed type annotation"""
    return float(sum(mxd_lst))
