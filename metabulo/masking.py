from metabulo.opencpu import opencpu_request


def mask_columns_by_group(table, groups, threshold):
    files = {
        'table': ('table.csv', table.to_csv().encode()),
        'groups': ('groups.csv', groups.to_csv().encode())
    }
    params = {
        'threshold': threshold
    }
    return opencpu_request('column_masks', files=files, params=params)
