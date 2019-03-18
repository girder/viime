<template lang="pug">
svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
  g.master
    g.axes
    g.plot
    g.ellipse(transform="translate(0, 0) rotate(0) scale(1, 1)")
      circle(cx="0",
             cy="0",
             r="1",
             style="fill: none; stroke: black;",
             vector-effect="non-scaling-stroke")
</template>

<script>
import { select } from 'd3-selection';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import 'd3-transition';

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
    points: {
      type: Array,
      required: true,
    },
  },
  watch: {
    points(newVal) {
      if (newVal) {
        this.update();
      }
    },
  },
  methods: {
    update() {
      // Grab the input props.
      const {
        width,
        height,
        points,
      } = this.$props;

      // Grab the root SVG element.
      const svg = select(this.$refs.svg);

      // Set a margin.
      const margin = {
        top: 20,
        right: 0,
        bottom: 20,
        left: 50,
      };

      const dwidth = width - margin.left - margin.right;
      const dheight = height - margin.top - margin.bottom;

      // Create X and Y axis objects.
      //
      // Scan the data for its range in X and Y.
      const xrange = minmax(points.map(d => d.x), 0.1);
      const yrange = minmax(points.map(d => d.y), 0.1);

      const scalex = scaleLinear()
        .domain(xrange)
        .range([0, dwidth]);

      const scaley = scaleLinear()
        .domain(yrange)
        .range([dheight, 0]);

      const xAxis = axisBottom(scalex);
      const yAxis = axisLeft(scaley);

      // Draw axes.
      const master = svg.select('g.master')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const axes = master.select('g.axes');

      const duration = 500;

      if (axes.select('.x-axis').size() === 0) {
        axes.append('g')
          .classed('x-axis', true)
          .attr('transform', `translate(0,${dheight})`)
          .call(xAxis);
      } else {
        axes.select('.x-axis')
          .transition()
          .duration(duration)
          .call(xAxis);
      }

      if (axes.select('.y-axis').size() === 0) {
        axes.append('g')
          .classed('y-axis', true)
          .call(yAxis);
      } else {
        axes.select('.y-axis')
          .transition()
          .duration(duration)
          .call(yAxis);
      }

      // Draw the data.
      //
      // Set up a colormap.
      const cmap = scaleOrdinal(['red', 'blue']);

      // Select an arbitrary label to color the points by.
      const label = Object.keys(points[0].labels)[0];

      // Plot the points in the scatter plot.
      select(this.$refs.svg)
        .select('g.plot')
        .selectAll('circle')
        .data(points)
        .join(enter => enter.append('circle')
          .attr('cx', (d, i, nodes) => 60000 * Math.cos(i * Math.PI / nodes.length))
          .attr('cy', (d, i, nodes) => 60000 * Math.sin(i * Math.PI / nodes.length))
          .attr('r', 0))
        .transition()
        .duration(duration)
        .delay((d, i) => i * 5)
        .attr('r', 2)
        .attr('cx', d => scalex(d.x))
        .attr('cy', d => scaley(d.y))
        .attr('fill', d => cmap(d.labels[label]));

      // Compute and display the data ellipse.
      const xs = points.map(d => d.x);
      const ys = points.map(d => d.y);

      const xMean = xs.reduce((acc, x) => acc + x, 0) / xs.length;
      const yMean = ys.reduce((acc, y) => acc + y, 0) / ys.length;

      const xx = covar(xs, xs);
      const yy = covar(ys, ys);
      const xy = covar(xs, ys);

      const trace = xx + yy;
      const det = xx * yy - xy * xy;

      const eigval = [
        trace / 2 + Math.sqrt(trace * trace / 4 - det),
        trace / 2 - Math.sqrt(trace * trace / 4 - det),
      ];

      const eigvec = Math.abs(xy) < 1e-10 ? [[1, 0], [0, 1]]
        : [[eigval[0] - yy, xy],
          [eigval[1] - yy, xy]];

      const rotation = Math.acos(eigvec[0][0]);

      select('g.ellipse')
        .transition()
        .duration(duration)
        .attr('transform', `translate(${scalex(xMean)}, ${scaley(yMean)}) rotate(${-180 * rotation / Math.PI}) scale(${0.5 * scalex(Math.sqrt(eigval[0]))}, ${0.5 * scaley(Math.sqrt(eigval[1]))})`);
    },
  },
};
</script>
