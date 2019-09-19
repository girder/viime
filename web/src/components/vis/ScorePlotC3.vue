<template lang="pug">
div
  div(ref="chart")
  span(style="display: none") {{ update }}
</template>

<style>
.c3 text {
  font-family: Barlow Condensed;
}
</style>

<script>
import c3 from 'c3';
import { select } from 'd3-selection';
import { deviation, mean } from 'd3-array';

import 'c3/c3.css';

function covar(xs, ys) {
  const e_xy = mean(xs.map((x, i) => x * ys[i]));
  const e_xx = mean(xs);
  const e_yy = mean(ys);

  return e_xy - e_xx * e_yy;
}

// Create a plot of the covariance confidence ellipse of `x` and `y`.
// x, y : array_like, shape (n, )
//     Input data.
// std : float
//     The number of standard deviations to determine the ellipse's radiuses.
//
// Port of Python function from:
//      https://matplotlib.org/gallery/statistics/confidence_ellipse.html
function confidenceEllipse(x, y, std) {
  // cov = np.cov(x, y)
  const xdev = deviation(x);
  const ydev = deviation(y);
  const xcov = xdev * xdev;
  const ycov = ydev * ydev;
  const xycov = covar(x, y);

  // pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
  const pearson = xycov / Math.sqrt(xcov * ycov);

  // # Using a special case to obtain the eigenvalues of this
  // # two-dimensionl dataset.
  // ell_radius_x = np.sqrt(1 + pearson)
  // ell_radius_y = np.sqrt(1 - pearson)
  const ell_radius_x = Math.sqrt(1 + pearson);
  const ell_radius_y = Math.sqrt(1 - pearson);

  // # Calculating the stdandard deviation of x from
  // # the squareroot of the variance and multiplying
  // # with the given number of standard deviations.
  // scale_x = np.sqrt(cov[0, 0]) * n_std
  // mean_x = np.mean(x)
  const scale_x = Math.sqrt(xcov) * std;
  const mean_x = mean(x);

  // # calculating the stdandard deviation of y ...
  // scale_y = np.sqrt(cov[1, 1]) * n_std
  // mean_y = np.mean(y)
  const scale_y = Math.sqrt(ycov) * std;
  const mean_y = mean(y);

  // transf = transforms.Affine2D() \
  //     .rotate_deg(45) \
  //     .scale(scale_x, scale_y) \
  //     .translate(mean_x, mean_y)
  const transform = `translate(${mean_x} ${mean_y}) scale(${scale_x} ${scale_y}) rotate(45)`;

  return { rx: ell_radius_x, ry: ell_radius_y, transform };
}

export default {
  props: {
    width: {
      type: Number,
      default: 400,
    },
    height: {
      type: Number,
      default: 300,
    },
    pcX: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    pcY: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    showEllipses: {
      type: Boolean,
      default: true,
    },
    pcCoords: {
      required: true,
      type: Array,
      validator: prop => prop.every(coord => coord.every(Number.isFinite)),
    },
    rowLabels: {
      required: true,
      type: Array,
      validator: prop => prop.every(val => typeof val === 'string'),
    },
    groupLabels: {
      required: true,
      type: Object,
    },
    eigenvalues: {
      required: true,
      type: Array,
      validator: prop => prop.every(Number.isFinite),
    },
    columns: {
      required: true,
      type: Array,
      validator: prop => prop.every(column => ['column_header', 'column_type'].every(key => Object.prototype.hasOwnProperty.call(column, key))),
    },
  },

  data() {
    return {
      chart: null,
      duration: 500,
    };
  },

  computed: {
    pcPoints() {
      const {
        pcCoords,
        pcX,
        pcY,
      } = this;

      const x = pcCoords.map(p => p[pcX - 1]);
      const y = pcCoords.map(p => p[pcY - 1]);

      return [x, y];
    },

    group() {
      const { columns } = this;
      const column = columns.find(elem => elem.column_type === 'group');

      return column.column_header;
    },

    valid() {
      const {
        pcCoords,
        rowLabels,
        groupLabels,
        eigenvalues,
      } = this;

      return this.$refs.chart
        && pcCoords.length > 0
        && rowLabels.length > 0
        && Object.keys(groupLabels).length > 0
        && eigenvalues.length > 0;
    },

    update() {
      const {
        pcCoords,
        pcPoints,
        pcX,
        pcY,
        showEllipses,
        duration,
        valid,
      } = this;

      if (!valid) {
        return '';
      }

      const x = `PC${pcX}`;
      const y = `PC${pcY}`;

      const [xData, yData] = pcPoints;

      const xGrouped = this.grouped(xData);
      const yGrouped = this.grouped(yData);

      const groups = Object.keys(xGrouped);
      const columns = [];
      const xs = {};
      groups.forEach((g) => {
        const xName = `${g}_x`;

        columns.push([xName, ...xGrouped[g]]);
        columns.push([g, ...yGrouped[g]]);

        xs[g] = xName;
      });

      // Draw the C3 chart.
      this.chart.load({
        columns,
        xs,
      });

      // Draw the data ellipses.
      const scaleX = this.chart.internal.x;
      const scaleY = this.chart.internal.y;
      const cmap = this.chart.internal.color;

      const confidenceEllipses = Object.keys(xGrouped).map(group => ({
        ...confidenceEllipse(xGrouped[group], yGrouped[group], 1),
        category: group,
      }));
      const xFactor = (scaleX(1e10) - scaleX(0)) / 1e10;
      const yFactor = (scaleY(1e10) - scaleY(0)) / 1e10;
      const plotTransform = `translate(${scaleX(0)} ${scaleY(0)}) scale(${xFactor} ${yFactor})`;
      select(this.$refs.chart)
        .select('.c3-custom-ellipses')
        .selectAll('ellipse')
        .data(confidenceEllipses)
        .join(
          enter => enter.append('ellipse')
            .attr('class', d => `ellipse-${d.category}`)
            .classed('ellipse', true)
            .style('fill', 'none')
            .style('stroke', d => cmap(d.category))
            .style('stroke-width', 1)
            .attr('vector-effect', 'non-scaling-stroke')
            .attr('rx', 0)
            .attr('ry', 0)
            .attr('transform', d => `${plotTransform} ${d.transform}`)
            .style('opacity', 1),
          update => update,
          exit => exit.transition('exit')
            .duration(duration)
            .style('opacity', 0)
            .remove(),
        )
        .transition('update')
        .duration(duration)
        .attr('rx', d => d.rx)
        .attr('ry', d => d.ry)
        .attr('transform', d => `${plotTransform} ${d.transform}`);

      this.setEllipseVisibility(showEllipses);

      return String(Math.random());
    },
  },

  mounted() {
    const {
      width,
      height,
    } = this;

    this.chart = c3.generate({
      bindto: this.$refs.chart,
      size: {
        width,
        height,
      },
      data: {
        columns: [],
        type: 'scatter',
      },
      axis: {
        x: {
          label: 'x',
          tick: {
            fit: false,
          },
        },
        y: {
          label: 'y',
        },
      },
      legend: {
        item: {
          onmouseover: (id) => {
            this.chart.focus(id);
            this.focusEllipse(id);
          },

          onmouseout: () => {
            this.chart.focus();
            this.focusEllipse();
          },
        },
      },
    });

    select(this.$refs.chart)
      .select('.c3-chart')
      .append('g')
      .classed('c3-custom-ellipses', true);
  },

  methods: {
    grouped(data) {
      const {
        groupLabels,
        group,
      } = this;

      const grouped = {};

      data.forEach((d, i) => {
        const g = groupLabels[group][i];

        if (!Object.prototype.hasOwnProperty.call(grouped, g)) {
          grouped[g] = [];
        }

        grouped[g].push(d);
      });

      return grouped;
    },

    focusEllipse(which) {
      const selector = which ? `ellipse.ellipse-${which}` : 'ellipse.ellipse';

      this.defocusEllipse();

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 1.0);
    },

    defocusEllipse(which) {
      const selector = which ? `ellipse.ellipse-${which}` : 'ellipse.ellipse';

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 0.3);
    },

    setEllipseVisibility(on) {
      const visible =
        select(this.$refs.chart).select('.ellipse').style('display') !== 'none';

      console.log(on, visible);
      if (on === visible) {
        return;
      }

      const opacity = on ? 1.0 : 0.0;

      const sel = select(this.$refs.chart)
        .selectAll('.ellipse');

      if (on) {
        sel.style('opacity', 0.0)
          .style('display', null);
      }

      const t = sel.transition()
        .duration(this.duration)
        .style('opacity', opacity);

      t.on('end', () => {
        if (!on) {
          sel.style('display', 'none')
            .style('opacity', 1.0);
        }
      });
    },
  },
};
</script>
