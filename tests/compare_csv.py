import csv
import math
import typing

# How close two floats have to be to be considered equal
float_diff = 1e-10


class CSV:
    """
    Represents a test CSV.

    This class makes it easy to compare Metaboanalyst CSVs with VIIME CSVs.
    """

    def __init__(self, csvfile: typing.Iterable[typing.Text]):
        reader = csv.reader(csvfile, quoting=csv.QUOTE_ALL)
        self._table = [row for row in reader]

        # Set up a map for row and column names to indices
        # This allows us to compare CSVs with different orderings
        self._row_map = {row[0]: index for (index, row) in enumerate(self._table[1:])}
        self._col_map = {name: index for (index, name) in enumerate(self._table[0][1:])}

        # Remove the header and label rows from the table
        self._table = [row[1:] for row in self._table[1:]]

    def __getitem__(self, args: (str, str)):
        row_name = args[0]
        col_name = args[1]
        row_index = self._row_map[row_name]
        col_index = self._col_map[col_name]
        return self._table[row_index][col_index]

    def __eq__(self, other):
        if self._col_map.keys() != other._col_map.keys():
            return False
        if self._row_map.keys() != other._row_map.keys():
            return False
        for row in self._row_map:
            for col in self._col_map:
                cell = self[row, col]
                other_cell = other[row, col]
                try:
                    if not math.isclose(float(cell), float(other_cell), rel_tol=float_diff):
                        return False
                except ValueError:
                    # float comparison failed, perhaps they are strings
                    if not cell == other_cell:
                        return False
        return True

    def get_pytest_error(self, other):
        if self._col_map.keys() != other._col_map.keys():
            return ['CSV headers match', f'{self._col_map.keys()} != {other._col_map.keys()}']
        if self._row_map.keys() != other._row_map.keys():
            return ['CSV row keys match', f'{self._row_map.keys()} != {other._row_map.keys()}']
        message = ['CSV contents match:']
        for row in self._row_map:
            for col in self._col_map:
                cell = self[row, col]
                other_cell = other[row, col]
                try:
                    if not math.isclose(float(cell), float(other_cell), rel_tol=float_diff):
                        message += [f'[{row}][{col}] {cell} != {other_cell}']
                except ValueError:
                    # float comparison failed, perhaps they are strings
                    if not cell == other_cell:
                        message += [f'[{row}][{col}] {cell} != {other_cell}']
        return message
