import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA


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


def pca(metabolites, metadata, x_component_index, y_component_index):
    n_components = max(x_component_index, y_component_index) + 1
    components = PCA(n_components=n_components).fit_transform(metabolites)
    samples = []
    for i in range(metabolites.shape[0]):
        samples.append({
            'x': components[i][x_component_index],
            'y': components[i][y_component_index],
            'key': metabolites.index[i],
            'labels': metadata.iloc[i].to_dict()
        })
    return samples
