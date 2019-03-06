import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from metabulo.models import TABLE_COLUMN_TYPES, TABLE_ROW_TYPES


def make_box_plot(frame):
    t = frame.to_records()
    data = []
    fig1, ax1 = plt.subplots()
    ax1.set_title('A plot')
    for a in t[1:]:
        arr = list(a)
        data.append(np.array(arr[2:]))
    ax1.boxplot(data)
    output = io.BytesIO()
    FigureCanvas(fig1).print_png(output)
    return output.getvalue()


def pca(frame, rows, columns, key):
    col_data_type = TABLE_COLUMN_TYPES.DATA
    column_data = filter(lambda col: col.column_type == col_data_type, columns)
    column_data_indexes = list(map(lambda col: col.column_index - 1, column_data))

    row_data_type = TABLE_ROW_TYPES.DATA
    row_data = filter(lambda row: row.row_type == row_data_type, rows)
    row_data_indexes = list(map(lambda row: row.row_index - 1, row_data))

    filtered = frame.iloc[row_data_indexes, column_data_indexes]
    label_column = frame.iloc[:, [int(key)]]
    label_column_dummies = pd.get_dummies(label_column).astype(int)

    n_components = min(len(row_data_indexes), label_column_dummies.shape[1])
    x = PCA(n_components=n_components).fit_transform(filtered)
    return [{'x': d[0], 'y': d[1], 'label': label_column.iloc[i][0]} for i, d in enumerate(x)]
