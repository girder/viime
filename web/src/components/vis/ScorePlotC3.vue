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

function unit(matrix) {
  return matrix.map((row) => {
    const mag = Math.sqrt(row[0] * row[0] + row[1] * row[1]);
    return row.map(d => d / mag);
  });
}

function dataEllipse(xs, ys, scaleX, scaleY) {
  // Compute the means.
  const xMean = xs.reduce((acc, x) => acc + x, 0) / xs.length;
  const yMean = ys.reduce((acc, y) => acc + y, 0) / ys.length;

  // Compute the covariance matrix. Note that "xy" = "yx" in this case so
  // we just compute xy.
  const xx = covar(xs, xs);
  const yy = covar(ys, ys);
  const xy = covar(xs, ys);

  // Compute the trace and determinant.
  const trace = xx + yy;
  const det = xx * yy - xy * xy;

  // Compute the eigenvalues and eigenvectors of the covariance matrix
  // according to
  // http://www.math.harvard.edu/archive/21b_fall_04/exhibits/2dmatrices/
  const eigval = [
    trace / 2 + Math.sqrt(trace * trace / 4 - det),
    trace / 2 - Math.sqrt(trace * trace / 4 - det),
  ];

  const eigvec = Math.abs(xy) < 1e-10 ? [[1, 0], [0, 1]]
    : unit([[eigval[0] - yy, xy],
      [eigval[1] - yy, xy]]);

  // Compute the rotation of the ellipse, mapping it into [-pi/2, pi/2].
  let rotation = Math.acos(eigvec[0][0]);
  if (rotation > Math.PI / 2) {
    rotation -= Math.PI;
  }

  // Compute the correct dimension of the ellipses.
  //
  // The ellipse major and minor axes are given in eigval, in *mixed units* of
  // the PCx and PCy axes. Therefore, it is not correct to use scaleX and scaleY
  // to determine their pixel extents.  Instead, we need a bit of geometry:
  // trigonometric identities together with the rotation angle will enable
  // calculating the x and y projections of the axes onto the PC axes, and then
  // the correct pixel size in the mixed direction can be calculated via
  // Pythagoras.
  const sq = x => x * x;
  const sin_t = Math.abs(Math.sin(rotation));
  const cos_t = Math.abs(Math.cos(rotation));

  const xPixels = v => scaleX(v) - scaleX(0);
  const yPixels = v => scaleY(v) - scaleY(0);
  const pixels = h => Math.sqrt(sq(xPixels(h * cos_t)) + sq(yPixels(h * sin_t)));

  return {
    xMean,
    yMean,
    rotation,
    axes: eigval.map(Math.sqrt).map(pixels),
  };
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
        valid,
      } = this;

      console.log(valid);
      if (!valid) {
        return '';
      }

      console.log(pcCoords);

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
      console.log('hey');
      console.log('chart', this.$refs.chart);
      if (!this.chart) {
        console.log('chart', this.$refs.chart);
        console.log('hi');
        this.chart = c3.generate({
          bindto: this.$refs.chart,
          size: {
            width: 600,
            height: 600,
          },
          data: {
            xs,
            columns,
            type: 'scatter',
          },
          axis: {
            x: {
              label: x,
              tick: {
                fit: false,
              },
            },
            y: {
              label: y,
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
      } else {
        console.log(this.chart);
        this.chart.load({
          columns,
          xs,
        });
      }

      // Draw the data ellipses.
      const scaleX = this.chart.internal.x;
      const scaleY = this.chart.internal.y;
      const cmap = this.chart.internal.color;

      const ellipses = Object.keys(xGrouped).map(group => ({
        ...dataEllipse(xGrouped[group], yGrouped[group], scaleX, scaleY),
        category: group,
      }));

      select(this.$refs.chart)
        .select('.c3-chart')
        .append('g')
        .classed('c3-custom-ellipses', true)
        .selectAll('g.ellipse')
        .data(ellipses)
        .enter()
        .append('g')
        .classed('ellipse', true)
        .attr('transform', d => `translate(${scaleX(d.xMean)}, ${scaleY(d.yMean)}) rotate(0) scale(1, 1)`)
        .append('circle')
        .attr('class', d => `ellipse-${d.category}`)
        .classed('ellipse', true)
        .attr('cx', 0)
        .attr('cy', 0)
        .attr('r', 1)
        .attr('style', 'fill: none; stroke: black;')
        .attr('vector-effect', 'non-scaling-stroke')
        .style('stroke', d => cmap(d.category));

      select(this.$refs.chart)
        .select('g.c3-custom-ellipses')
        .selectAll('g.ellipse')
        .data(ellipses)
        .transition()
        .duration(this.duration)
        .attr('transform', (d) => {
          const xMean = scaleX(d.xMean);
          const yMean = scaleY(d.yMean);
          const rotation = -180 * d.rotation / Math.PI;

          return `translate(${xMean}, ${yMean}) rotate(${rotation}) scale(${d.axes[0]}, ${d.axes[1]})`;
        });

      this.setEllipseVisibility(showEllipses);

      const confidenceEllipses = Object.keys(xGrouped).map(group => ({
        ...confidenceEllipse(xGrouped[group], yGrouped[group], 1),
        category: group,
      }));
      const xFactor = (scaleX(1e10) - scaleX(0)) / 1e10;
      const yFactor = (scaleY(1e10) - scaleY(0)) / 1e10;
      const plotTransform = `translate(${scaleX(0)} ${scaleY(0)}) scale(${xFactor} ${yFactor})`;
      select(this.$refs.chart)
        .select('.c3-chart')
        .append('g')
        .classed('c3-custom-ellipses', true)
        .selectAll('ellipse')
        .data(confidenceEllipses)
        .enter()
        .append('ellipse')
        .style('fill', 'none')
        .style('stroke', d => cmap(d.category))
        .style('stroke-width', 2)
        .attr('rx', d => d.rx)
        .attr('ry', d => d.ry)
        .attr('vector-effect', 'non-scaling-stroke')
        .attr('transform', d => `${plotTransform} ${d.transform}`);

      return String(Math.random());
    },
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
      const selector = which ? `circle.ellipse-${which}` : 'circle.ellipse';

      this.defocusEllipse();

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 1.0);
    },

    defocusEllipse(which) {
      const selector = which ? `circle.ellipse-${which}` : 'circle.ellipse';

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 0.3);
    },

    setEllipseVisibility(on) {
      const opacity = on ? 1.0 : 0.0;

      select(this.$refs.chart)
        .selectAll('circle.ellipse')
        .transition()
        .duration(this.duration)
        .style('opacity', opacity);
    },
  },
};
</script>
