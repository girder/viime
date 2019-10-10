"""
This module contains methods related to mergind dataset
"""
from typing import List

import pandas

from viime.models import ValidatedMetaboliteTable


def simple_merge(validated_tables: List[ValidatedMetaboliteTable]):
    """
    Generate a new validated csv file by concatonating a list of 2 or more
    validated tables.

    NOTE: This current uses the groups from the first table, removes
    all of the metadata, and does and "inner join" with the row indices
    """
    tables = []

    for index, table in enumerate(validated_tables):
        if index == 0:
            groups = table.groups

        tables.append(table.measurements)

    return pandas.concat([groups] + tables, axis=1, join='inner')
