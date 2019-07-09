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
  position: fixed;
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
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';

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
    points: {
      required: true,
      validator: prop => !prop
          || (typeof prop === 'object'
          && prop.every(val => ['x', 'y', 'col'].every(key => key in val))),
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
      xrange: [-1.2, 1.2],
      yrange: [-1.2, 1.2],
      duration: 500,
    };
  },
  computed: {
    group() {
      const { dataset } = this;
      const column = dataset._source.columns.find(elem => elem.column_type === 'group');

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
    const svg = select(this.$refs.svg);
    this.axisPlot(svg);
    this.setXLabel('PC1 correlation');
    this.setYLabel('PC2 correlation');
    if (this.points) {
      this.update();
    }
  },
  methods: {
    update() {
      // Grab the input props.
      const {
        points,
      } = this.$props;

      // Plot the vectors as a scatter plot.
      const svg = select(this.$refs.svg);
      const tooltip = select(this.$refs.tooltip);
      const coordFormat = format('.2f');
      const radius = 5;
      svg.select('g.plot')
        .selectAll('circle')
        .data(points)
        .join(enter => enter.append('circle')
          .attr('cx', this.scaleX(0))
          .attr('cy', this.scaleY(0))
          .attr('r', 0)
          .style('fill-opacity', 0.001)
          .style('stroke', 'black')
          .on('mouseover', function mouseover(d) {
            select(this)
              .transition()
              .duration(200)
              .attr('r', 2 * radius);

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
              .attr('r', radius);

            tooltip.transition()
              .duration(500)
              .style('opacity', 0.0);
          }))
        .transition()
        .duration(this.duration)
        .delay((d, i) => i * 5)
        .attr('r', radius)
        .attr('cx', d => this.scaleX(d.x))
        .attr('cy', d => this.scaleY(d.y));
    },
  },
};
</script>
