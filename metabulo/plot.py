import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np


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
