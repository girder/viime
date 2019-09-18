import numpy as np

SCALING_METHODS = {'auto', 'range', 'pareto', 'vast', 'level'}


def scale(method, table):
    if method is None:
        pass
    elif method == 'auto':
        table = auto(table)
    elif method == 'range':
        table = range(table)
    elif method == 'pareto':
        table = pareto(table)
    elif method == 'vast':
        table = vast(table)
    elif method == 'level':
        table = level(table)
    else:
        raise Exception('Unknown scaling method')
    return table


def center(table):
    return table - table.mean()


def auto(table):
    return center(table) / table.std()


def range(table):
    return center(table) / (table.max() - table.min())


def pareto(table):
    return center(table) / np.sqrt(table.std())


def vast(table):
    mean = table.mean()
    sd = table.std()
    return (mean / sd) * (table - mean) / sd


def level(table):
    mean = table.mean()
    return (table - mean) / mean
