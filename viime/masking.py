import pandas as pd

from viime.opencpu import opencpu_request


def mask_columns_by_group(table: pd.DataFrame, groups: pd.DataFrame,
                          threshold: float) -> pd.DataFrame:
    files = {
        'table': ('table.csv', table.to_csv().encode()),
        'groups': ('groups.csv', groups.to_csv().encode())
    }
    params = {
        'threshold': threshold
    }
    return opencpu_request('column_masks', files=files, params=params)
