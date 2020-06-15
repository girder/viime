<template lang="pug">
.main(v-resize:throttle="onResize")
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.label.x(style="opacity: 0")
        text x
      g.label.y(style="opacity: 0")
        text y
      g.crosshairs
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
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';

function domain(arr) {
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  arr.forEach((v) => {
    if (v < min) {
      min = v;
    }
    if (v > max) {
      max = v;
    }
  });
  const amax = Math.max(Math.abs(max), Math.abs(min));
  return [-amax, amax];
}

export default {
  mixins: [
    axisPlot,
  ],
  props: {
    points: {
      required: true,
      validator: (prop) => !prop
          || (typeof prop === 'object'
          && prop.every((val) => ['col', 'loadings'].every((key) => key in val))),
    },
    pcX: {
      default: 1,
      validator: Number.isInteger,
    },
    pcY: {
      default: 2,
      validator: Number.isInteger,
    },
    showCrosshairs: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      margin: {
        top: 20,
        right: 20,
        bottom: 50,
        left: 50,
      },
      fadeInDuration: 500,
      duration: 200,
    };
  },
  computed: {
    pointsInternal() {
      return this.points || [];
    },
    pcXRange() {
      const {
        pointsInternal,
        pcX,
      } = this;
      const arr = pointsInternal.map((d) => d.loadings[pcX - 1]);
      if (arr.length === 0) {
        return [-1, 1];
      }
      return domain(arr);
    },
    pcYRange() {
      const {
        pointsInternal,
        pcY,
      } = this;
      const arr = pointsInternal.map((d) => d.loadings[pcY - 1]);
      if (arr.length === 0) {
        return [-1, 1];
      }
      return domain(arr);
    },
    pcRange() {
      const x = this.pcXRange;
      const y = this.pcYRange;
      return [Math.min(x[0], y[0]), Math.max(x[1], y[1])];
    },
    xrange() {
      return this.pcRange;
    },
    yrange() {
      return this.pcRange;
    },
  },
  watch: {
    points() {
      this.update();
    },
    pcX() {
      this.update();
    },
    pcY() {
      this.update();
    },
    showCrosshairs() {
      this.update();
    },
  },
  methods: {
    update() {
      // Grab the input props.
      const {
        pointsInternal,
        pcX,
        pcY,
        showCrosshairs,
      } = this;

      if (pointsInternal.length === 0
        || pointsInternal[0].loadings.length < pcX
        || pointsInternal[0].loadings.length < pcY) {
        return;
      }

      // Plot the vectors as a scatter plot.
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);
      this.setXLabel(`PC${pcX} correlation`);
      this.setYLabel(`PC${pcY} correlation`);
      const tooltip = select(this.$refs.tooltip);
      const coordFormat = format('.2f');
      const radius = 4;
      const { duration } = this;

      const crosshair = {
        color: 'gray',
        width: '2px',
      };
      svg
        .select('g.crosshairs')
        .selectAll('line')
        .data([{ x: 10, y: 0 }, { x: 0, y: 10 }])
        .join((enter) => enter.append('line')
          .attr('stroke', crosshair.color)
          .attr('stroke-width', crosshair.width))
        .style('display', showCrosshairs ? null : 'none')
        .attr('x1', (d) => this.scaleX(0) - d.x)
        .attr('x2', (d) => this.scaleX(0) + d.x)
        .attr('y1', (d) => this.scaleY(0) - d.y)
        .attr('y2', (d) => this.scaleY(0) + d.y);

      svg.select('g.plot')
        .selectAll('circle')
        .data(pointsInternal)
        .join((enter) => enter.append('circle')
          .attr('cx', this.scaleX(0))
          .attr('cy', this.scaleY(0))
          .attr('r', 0)
          .style('fill-opacity', 0.001)
          .style('stroke', 'black')
          .on('mouseover', function mouseover(d) {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', 2 * radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9);
            tooltip.html(`<b>${d.col}</b><br>(${coordFormat(d.loadings[pcX - 1])}, ${coordFormat(d.loadings[pcY - 1])})`)
              .style('left', `${event.clientX + 15}px`)
              .style('top', `${event.pageY - 30}px`);
          })
          .on('mouseout', function mouseout() {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.0);
          }))
        .transition()
        .duration(this.fadeInDuration)
        .attr('r', radius)
        .attr('cx', (d) => this.scaleX(d.loadings[pcX - 1]))
        .attr('cy', (d) => this.scaleY(d.loadings[pcY - 1]));
    },
  },
};
</script>
