<template>
  <svg ref="svg" :width="width" :height="height" xmlns="http://www.w3.org/2000/svg">
    <g class="master">
      <g class="axes"></g>
      <g class="plot"></g>
    </g>
  </svg>
</template>

<script>
import { select } from 'd3-selection';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import 'd3-transition';

function minmax (data, padding = 0.0) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const pad = padding * (max - min);

  return [
    min - pad,
    max + pad,
  ];
}

export default {
  props: {
    width: Number,
    height: Number,
    points: Array,
  },
  watch: {
    points (newVal) {
      if (newVal) {
        this.update();
      }
    },
  },
  methods: {
    update () {
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

      const x = scaleLinear()
        .domain(xrange)
        .range([0, dwidth]);

      const y = scaleLinear()
        .domain(yrange)
        .range([dheight, 0]);

      const xAxis = axisBottom(x);
      const yAxis = axisLeft(y);

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
      const cmap = scaleOrdinal(['red', 'blue']);
      let plot = select(this.$refs.svg)
        .select('g.plot')
        .selectAll('circle')
        .data(points)
        .join(enter => enter.append('circle')
          .attr('cx', (d, i, nodes) => 60000 * Math.cos(i * Math.PI / nodes.length))
          .attr('cy', (d, i, nodes) => 60000 * Math.sin(i * Math.PI / nodes.length))
          .attr('r', 0)
        )
        .transition()
        .duration(duration)
        .delay((d, i) => i * 5)
        .attr('r', 2)
        .attr('cx', d => x(d.x))
        .attr('cy', d => y(d.y))
        .attr('fill', d => cmap(d.labels[1]))
    }
  },
};
</script>
