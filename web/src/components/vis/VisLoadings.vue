<template lang="pug">
div
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.label.x(style="opacity: 0")
        text x
      g.label.y(style="opacity: 0")
        text y
      g.plot
  .tooltip(ref="tooltip")
</template>

<style scoped lang="scss">
div.tooltip {
  position: absolute;
  text-align: center;
  width: 120px;
  height: 45px;
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

function minmax(data, padding = 0.0) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const pad = padding * (max - min);

  return [
    min - pad,
    max + pad,
  ];
}

function axisLabel(which, msg, label, x, y, rot) {
  const text = label.select('text')
    .html(`${msg}`);
  const bbox = text.node().getBBox();
  label.attr('transform', `translate(${x(bbox)},${y(bbox)}) rotate(${rot})`)
    .style('opacity', 1.0);
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
      required: true,
      validator: prop => !prop
          || (typeof prop === 'object'
          && prop.every(val => ['x', 'y', 'col'].every(key => key in val))),
    },
  },
  computed: {
    group() {
      const { dataset } = this;
      const column = dataset.source.columns.find(elem => elem.column_type === 'group');

      return column.column_header;
    },
  },
  watch: {
    points(newval) {
      if (newval) {
        this.update();
      }
    },
  },
  mounted() {
    if (this.points) {
      this.update();
    }
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
        bottom: 50,
        left: 50,
      };

      const dwidth = width - margin.left - margin.right;
      const dheight = height - margin.top - margin.bottom;

      // Create X and Y axis objects.
      const xrange = minmax([-1, 1], 0.1);
      const yrange = minmax([-1, 1], 0.1);

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
          .attr('transform', `translate(0,0)`)
          .call(yAxis);
      } else {
        axes.select('.y-axis')
          .transition()
          .duration(duration)
          .call(yAxis);
      }

      axisLabel(1,
        'x correlation',
        svg.select('.label.x'),
        bbox => dwidth / 2 - bbox.width / 2,
        bbox => dheight + margin.bottom / 2 + bbox.height / 2,
        0);

      axisLabel(2,
        'y correlation',
        svg.select('.label.y'),
        bbox => -margin.left / 2 - bbox.height / 2,
        bbox => dheight / 2 + bbox.width / 2,
        -90);

      // Draw the data.
      //
      // Plot the vectors and points in the scatter plot.
      const sel = svg.select('g.plot');
      sel.selectAll('line')
        .data(points)
        .join(enter => enter.append('line')
          .attr('x1', scalex(0))
          .attr('y1', scaley(0))
          .attr('x2', scalex(0))
          .attr('y2', scaley(0))
          .style('stroke', 'black')
          .style('opacity', 0.0))
        .transition()
        .duration(duration)
        .attr('x2', d => scalex(d.x))
        .attr('y2', d => scaley(d.y))
        .style('opacity', 1.0);

      const tooltip = select(this.$refs.tooltip);
      const coordFormat = format('.2f');
      sel.selectAll('circle')
        .data(points)
        .join(enter => enter.append('circle')
          .attr('cx', scalex(0))
          .attr('cy', scaley(0))
          .attr('r', 0)
          .on('mouseover', function mouseover(d) {
            select(this)
              .transition()
              .duration(200)
              .attr('r', 4);

            tooltip.transition()
              .duration(200)
              .style('opacity', 0.9);
            tooltip.html(`col: ${d.col}<br>x corr: ${coordFormat(d.x)}<br>y corr: ${coordFormat(d.y)}`)
              .style('left', `${event.clientX}px`)
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
        .duration(duration)
        .delay((d, i) => i * 5)
        .attr('r', 2)
        .attr('cx', d => scalex(d.x))
        .attr('cy', d => scaley(d.y));
    },
  },
};
</script>
