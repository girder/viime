from itertools import cycle
from typing import Iterator

# d3 scheme category 10
_category10 = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
               '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e']
_scheme_set3 = ['#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
                '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f']


def category10() -> Iterator[str]:
    return cycle(_category10)


def scheme_set3() -> Iterator[str]:
    return cycle(_scheme_set3)
