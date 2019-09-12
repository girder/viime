<template lang="pug">
div
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.label.x
        text {{ xlabel }}
      g.label.y
        text {{ ylabel }}
      g.plot
  .tooltip(ref="tooltip")
</template>

<style scoped>
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
import { scalePoint } from 'd3-scale';
import { select } from 'd3-selection';
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
    eigenvalues: {
      required: true,
      type: Array,
      validator: prop => prop.every(v => Number.isFinite(v) && v > 0.0)
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
      xlabel: 'Principal Component',
      ylabel: 'Eigenvalue',
    };
  },

  computed: {
    scaleX() {
      const {
        eigenvalues,
        dwidth,
      } = this;

      const labels = [...Array(eigenvalues.length).keys()].map(d => d + 1);

      return scalePoint()
        .domain(labels)
        .range([0, dwidth]);
    },

    yrange() {
      const {
        eigenvalues,
      } = this;

      return [0.0, Math.max(...eigenvalues) * 1.1];
    },
  },

  mounted() {
    const svg = select(this.$refs.svg);
    this.axisPlot(svg);

    this.setXLabel(this.xlabel);
    this.setYLabel(this.ylabel);

    this.update();
  },

  methods: {
    update() {
      const {
        eigenvalues,
        fadeInDuration,
        duration,
      } = this;

      const radius = 4;

      const svg = select(this.$refs.svg);
      const tooltip = select(this.$refs.tooltip);

      svg.select('g.plot')
        .selectAll('circle')
        .data(eigenvalues)
        .join(enter => enter.append('circle')
          .attr('cx', this.scaleX(1))
          .attr('cy', this.scaleY(0))
          .attr('r', 0)
          .style('stroke', 'black')
          .style('fill-opacity', 0.001)
          .on('mouseover', function mouseover(d, i) {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', 2 * radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9)

            tooltip.html(`<b>Eigenvalue:</b> ${d}`)
              .style('left', `${event.clientX + 15}px`)
              .style('top', `${event.clientY - 30}px`);

          })
          .on('mouseout', function mouseout() {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.0);
          })
        )
        .transition()
        .duration(fadeInDuration)
        .attr('r', radius)
        .attr('cx', (d, i) => this.scaleX(i + 1))
        .attr('cy', d => this.scaleY(d));
    },
  },

};
</script>
