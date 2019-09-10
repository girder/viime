<template lang="pug">
div
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.label.x(style="opacity: 0")
        text PC1 (0%)
      g.label.y(style="opacity: 0")
        text PC2 (0%)
      g.ellipses
      g.plot
  .tooltip(ref="tooltip")
</template>

<style scoped lang="scss">
div.tooltip {
  position: fixed;
  text-align: center;
  padding: 2px;
  background: #eee;
  border: 0px;
  border-radius: 3px;
  pointer-events: none;
  z-index: 20;
  opacity: 0;
}
</style>

<script>
import { select, event } from 'd3-selection';
import { format } from 'd3-format';
import { scaleOrdinal } from 'd3-scale';
import { schemeCategory10 } from 'd3-scale-chromatic';
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';

function minmax(data, padding = 0.0) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const pad = padding * (max - min);

  return [
    min - pad,
    max + pad,
  ];
}

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

export default {
  mixins: [
    axisPlot,
  ],
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
    /* {{
     *   x: Array<Array<Number>>,
     *   labels: Object<string, Array<string>>
     * }}
     */
    rawPoints: {
      required: true,
      validator: prop => !prop
          || (typeof prop === 'object' && ['x', 'labels'].every(key => key in prop)),
    },
    dataset: {
      required: true,
      validator: prop => typeof prop === 'object'
        && '_source' in prop
        && typeof prop._source === 'object'
        && 'columns' in prop._source
        && Array.isArray(prop._source.columns),
    },
  },
  data() {
    return {
      margin: {
        top: 20,
        right: 0,
        bottom: 50,
        left: 50,
      },
      xrange: [-1, 1],
      yrange: [-1, 1],
      fadeInDuration: 500,
      duration: 200,
    };
  },
  computed: {
    xlabel() {
      return `PC${this.pcX}`;
    },

    ylabel() {
      return `PC${this.pcY}`;
    },

    xyPoints() {
      const {
        rawPoints,
        pcX,
        pcY,
      } = this;

      if (rawPoints) {
        return rawPoints.x.map(p => ({
          x: p[pcX - 1],
          y: p[pcY - 1],
        }));
      }

      return null;
    },
    rowLabels() {
      return this.rawPoints.rows;
    },
    group() {
      const { dataset } = this;
      const column = dataset._source.columns.find(elem => elem.column_type === 'group');

      return column.column_header;
    },
  },
  watch: {
    pcX() {
      this.update();
    },

    pcY() {
      this.update();
    },

    showEllipses() {
      this.update();
    },

    rawPoints(newval) {
      if (newval) {
        if (!this.axisPlotInitialized) {
          const { xyPoints } = this;
          this.setRanges(xyPoints);
          const svg = select(this.$refs.svg);
          this.axisPlot(svg);
        }
        this.update();
      }
    },
  },
  mounted() {
    const {
      xyPoints,
    } = this;

    if (xyPoints) {
      this.setRanges(xyPoints);
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);
      this.update();
    }
  },
  methods: {
    setRanges(xyPoints) {
      this.xrange = minmax(xyPoints.map(p => p.x), 0.1);
      this.yrange = minmax(xyPoints.map(p => p.y), 0.1);
    },
    update() {
      // Grab the input props.
      const {
        rawPoints,
        xyPoints,
        group,
        xlabel,
        ylabel,
        pcX,
        pcY,
        showEllipses,
      } = this;

      // Set the axis labels.
      //
      // Compute the total variance in all the PCs.
      const totVariance = rawPoints.sdev.reduce((acc, x) => acc + x, 0);
      const pctFormat = format('.2%');
      const svg = select(this.$refs.svg);
      this.setRanges(xyPoints);
      this.axisPlot(svg);
      this.setXLabel(`${xlabel} (${pctFormat(rawPoints.sdev[pcX - 1] / totVariance)})`);
      this.setYLabel(`${ylabel} (${pctFormat(rawPoints.sdev[pcY - 1] / totVariance)})`);

      // Draw the data.
      //
      // Set up a colormap and select an arbitrary label to color the nodes.
      const cmap = scaleOrdinal(schemeCategory10);

      // Plot the points in the scatter plot.
      const tooltip = select(this.$refs.tooltip);
      const coordFormat = format('.2f');
      const radius = 4;
      const {
        rowLabels,
        duration,
      } = this;
      svg.select('g.plot')
        .selectAll('circle')
        .data(xyPoints)
        .join(enter => enter.append('circle')
          .attr('cx', this.scaleX(0))
          .attr('cy', this.scaleY(0))
          .attr('r', 0)
          .style('stroke', (d, i) => (group ? cmap(rawPoints.labels[group][i]) : null))
          .style('fill-opacity', 0.001)
          .on('mouseover', function mouseover(d, i) {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', 2 * radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9);
            tooltip.html(`<b>${rowLabels[i]}</b><br>(${coordFormat(d.x)}, ${coordFormat(d.y)})`)
              .style('left', `${event.clientX + 15}px`)
              .style('top', `${event.clientY - 30}px`);
          })
          .on('mouseout', function mouseout() {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', radius);

            tooltip.transition()
              .duration(this.duration)
              .style('opacity', 0.0);
          }))
        .transition()
        .duration(this.fadeInDuration)
        .attr('r', radius)
        .attr('cx', d => this.scaleX(d.x))
        .attr('cy', d => this.scaleY(d.y));

      // Decompose the data into its label categories.
      const streams = {};
      xyPoints.forEach((p, i) => {
        const category = rawPoints.labels[group][i];
        if (!streams[category]) {
          streams[category] = [];
        }
        streams[category].push(p);
      });

      // Compute the ellipse data for each subset.
      if (showEllipses) {
        const ellipses = [];
        Object.keys(streams).forEach((category) => {
          const data = streams[category];

          const xs = data.map(d => d.x);
          const ys = data.map(d => d.y);

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

          // Compute the rotation of the ellipse, taking into account the quadrant
          // the eigenvectors are pointing into.
          const rotation = Math.sign(eigvec[0][1]) * Math.acos(eigvec[0][0]);

          ellipses.push({
            xMean,
            yMean,
            rotation,
            eigval,
            category,
          });
        });

        // Draw the ellipses.
        svg.select('g.ellipses')
          .selectAll('g.ellipse')
          .data(ellipses)
          .enter()
          .append('g')
          .classed('ellipse', true)
          .attr('transform', d => `translate(${this.scaleX(d.xMean)}, ${this.scaleY(d.yMean)}) rotate(0) scale(1, 1)`)
          .append('circle')
          .attr('cx', 0)
          .attr('cy', 0)
          .attr('r', 1)
          .attr('style', 'fill: none; stroke: black;')
          .attr('vector-effect', 'non-scaling-stroke')
          .style('stroke', d => cmap(d.category));

        svg.select('g.ellipses')
          .selectAll('g.ellipse')
          .data(ellipses)
          .transition()
          .duration(this.duration)
          .attr('transform', (d) => {
            const xMean = this.scaleX(d.xMean);
            const yMean = this.scaleY(d.yMean);
            const rotation = -180 * d.rotation / Math.PI;
            const xScale = this.scaleX(Math.sqrt(d.eigval[0])) - this.scaleX(0);
            const yScale = this.scaleY(Math.sqrt(d.eigval[1])) - this.scaleY(0);

            return `translate(${xMean}, ${yMean}) rotate(${rotation}) scale(${xScale}, ${yScale})`;
          });
      } else {
        svg.select('g.ellipses')
          .selectAll('*')
          .transition()
          .duration(this.duration)
          .style('opacity', 0.0)
          .remove();
      }
    },
  },
};
</script>