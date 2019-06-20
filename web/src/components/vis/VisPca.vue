<template lang="pug">
div
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.label.x(style="opacity: 0")
        text PC1 (0%)
      g.label.y(style="opacity: 0")
        text PC2 (0%)
      g.plot
      g.ellipses
  .tooltip(ref="tooltip")
</template>

<style scoped lang="scss">
div.tooltip {
  position: absolute;
  text-align: center;
  width: 120px;
  height: 30px;
  padding: 2px;
  font: 12px sans-serif;
  background: lightsteelblue;
  border: 0px;
  border-radius: 3px;
  pointer-events: none;
  opacity: 0;
}
</style>

<script>
import { select, event } from 'd3-selection';
import { format } from 'd3-format';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { schemeCategory10 } from 'd3-scale-chromatic';
import { axisBottom, axisLeft } from 'd3-axis';
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
        && 'source' in prop
        && typeof prop.source === 'object'
        && 'columns' in prop.source
        && Array.isArray(prop.source.columns),
    },
  },
  computed: {
    xyPoints() {
      if (this.rawPoints) {
        return this.rawPoints.x.map(p => ({
          x: p[0],
          y: p[1],
        }));
      } else {
        return null;
      }
    },
    group() {
      const { dataset } = this;
      const column = dataset.source.columns.find(elem => elem.column_type === 'group');

      return column.column_header;
    },
  },
  watch: {
    rawPoints(newval) {
      if (newval) {
        if (!this.axisPlotInitialized) {
          const xyPoints = this.xyPoints;
          this.axisPlot({
            margin: {
              top: 20,
              right: 0,
              bottom: 50,
              left: 50,
            },
            xrange: minmax(xyPoints.map(p => p.x), 0.1),
            yrange: minmax(xyPoints.map(p => p.y), 0.1),
            xlabel: 'PC1',
            ylabel: 'PC2',
            duration: 500,
          });
        }

        this.update();
      }
    },
  },
  mounted() {
    if (this.xyPoints) {
      const xyPoints = this.xyPoints;
      this.axisPlot({
        margin: {
          top: 20,
          right: 0,
          bottom: 50,
          left: 50,
        },
        xrange: minmax(xyPoints.map(p => p.x), 0.1),
        yrange: minmax(xyPoints.map(p => p.y), 0.1),
        xlabel: 'PC1',
        ylabel: 'PC2',
        duration: 500,
      });

      this.update();
    }
  },
  methods: {
    update() {
      // Grab the input props.
      const {
        rawPoints,
      } = this.$props;

      const xyPoints = this.xyPoints;

      // Set the axis labels.
      //
      // Compute the total variance in all the PCs.
      const totVariance = rawPoints.sdev.reduce((acc, x) => acc + x, 0);
      const pctFormat = format('.2%');
      this.setXLabel(`PC1 (${pctFormat(rawPoints.sdev[0] / totVariance)})`);
      this.setYLabel(`PC2 (${pctFormat(rawPoints.sdev[1] / totVariance)})`);

      // Draw the data.
      //
      // Plot the points in the scatter plot.
      const tooltip = select(this.$refs.tooltip);
      const coordFormat = format('.2f');
      const sel = this.svg.select('g.plot')
        .selectAll('circle')
        .data(xyPoints)
        .join(enter => enter.append('circle')
          .attr('cx', (d, i, nodes) => 60000 * Math.cos(i * Math.PI / nodes.length))
          .attr('cy', (d, i, nodes) => 60000 * Math.sin(i * Math.PI / nodes.length))
          .attr('r', 0)
          .on('mouseover', function mouseover(d) {
            select(this)
              .transition()
              .duration(200)
              .attr('r', 4);

            tooltip.transition()
              .duration(200)
              .style('opacity', 0.9);
            tooltip.html(`PC1: ${coordFormat(d.x)}<br>PC2: ${coordFormat(d.y)}`)
              .style('left', `${event.pageX}px`)
              .style('top', `${event.pageY - 30}px`);
          })
          .on('mouseout', function mouseout() {
            select(this)
              .transition()
              .duration(500)
              .attr('r', 2);

            tooltip.transition()
              .duration(500)
              .style('opacity', 0.0);
          }))
        .transition()
        .duration(this.duration)
        .delay((d, i) => i * 5)
        .attr('r', 2)
        .attr('cx', d => this.scaleX(d.x))
        .attr('cy', d => this.scaleY(d.y));

      // Set up a colormap and select an arbitrary label to color the nodes.
      const cmap = scaleOrdinal(schemeCategory10);
      const label = this.group;
      if (label) {
        sel.transition()
          .duration(this.duration)
          .attr('fill', (d, i) => cmap(rawPoints.labels[label][i]));
      }

      // Decompose the data into its label categories.
      const streams = {};
      xyPoints.forEach((p, i) => {
        const category = rawPoints.labels[label][i];
        if (!streams[category]) {
          streams[category] = [];
        }
        streams[category].push(p);
      });

      // Compute the ellipse data for each subset.
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
      this.svg.select('g.ellipses')
        .selectAll('g.ellipse')
        .data(ellipses)
        .enter()
        .append('g')
        .classed('ellipse', true)
        .attr('transform', 'translate(0, 0) rotate(0) scale(1, 1)')
        .append('circle')
        .attr('cx', 0)
        .attr('cy', 0)
        .attr('r', 1)
        .attr('style', 'fill: none; stroke: black;')
        .attr('vector-effect', 'non-scaling-stroke')
        .style('stroke', d => cmap(d.category));

      this.svg.select('g.ellipses')
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
    },
  },
};
</script>
