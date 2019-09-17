<template lang="pug">
div
  div(ref="chart")
  span(style="display: none") {{ update }}
</template>

<script>
import c3 from 'c3';
import { select } from 'd3-selection';

import 'c3/c3.css';

function covar(xs, ys) {
  const sum = arr => arr.reduce((acc, x) => acc + x, 0);
  const mean = arr => sum(arr) / arr.length;

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
      validator: prop => Object.values(prop).every(labels => labels.every(val => typeof val === 'string')),
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

    update() {
      const {
        pcCoords,
        pcPoints,
        pcX,
        pcY,
      } = this;

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
      this.chart = window.chart = c3.generate({
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
              console.log('legend', id);
              this.chart.focus(id);

              select(this.$refs.chart)
                .selectAll('circle.ellipse')
                .style('opacity', 0.3);

              select(this.$refs.chart)
                .select(`circle.ellipse-${id}`)
                .style('opacity', 1.0);
            },

            onmouseout: () => {
              this.chart.focus();
              select(this.$refs.chart)
                .selectAll('circle.ellipse')
                .style('opacity', 1.0);
            },
          },
        },
      });

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

      return String(Math.random());
    },
  },

  methods: {
    grouped(data) {
      const {
        groupLabels,
        group,
      } = this;

      console.log(groupLabels, group);

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
  },
};
</script>
