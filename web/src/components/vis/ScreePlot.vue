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
        path.line
        g.points
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

path.line {
  fill: none;
  stroke: black;
}
</style>

<script>
import { scalePoint } from 'd3-scale';
import { select } from 'd3-selection';
import { format } from 'd3-format';
import { line } from 'd3-shape';
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';

const sum = arr => arr.reduce((acc, x) => acc + x, 0);

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
    numComponents: {
      default: 10,
      type: Number,
      validator: Number.isInteger,
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
        numComponents,
        dwidth,
      } = this;

      const labels = [...Array(numComponents).keys()].map(d => d + 1);

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

    percents() {
      const total = sum(this.eigenvalues);
      return this.eigenvalues.map(d => d / total);
    },

    cumulativePercents() {
      const result = [0, ...this.percents];
      for (let i = 1; i < result.length; i++) {
        result[i] += result[i - 1];
      }

      return result.slice(1);
    },
  },

  watch: {
    numComponents() {
      this.update();
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
        percents,
        cumulativePercents,
        fadeInDuration,
        duration,
        numComponents,
      } = this;

      const radius = 4;

      const svg = select(this.$refs.svg);
      const tooltip = select(this.$refs.tooltip);

      const data = eigenvalues.map((d, i) => ({
        eigenvalue: d,
        percent: percents[i],
        cumPercent: cumulativePercents[i],
      })).slice(0, numComponents);

      const pctFormat = format('.2%');
      const floatFormat = format('.2f');

      this.axisPlot(svg);
      svg.select('g.points')
        .selectAll('circle')
        .data(data)
        .join(enter => enter.append('circle')
          .attr('cx', (d, i) => this.scaleX(i + 1))
          .attr('cy', this.scaleY(0))
          .attr('r', 0)
          .style('stroke', 'black')
          .style('fill', 'white')
          .style('fill-opacity', 1.0)
          .on('mouseover', function mouseover(d, i) {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', 2 * radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9)

            const eig = floatFormat(d.eigenvalue);
            const pct = pctFormat(d.percent);
            const cpct = pctFormat(d.cumPercent);

            tooltip.html(`<b>Principal Component ${i + 1}</b><br>${eig}<br>${pct} total variance<br>(${cpct} cumulative)`)
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
        .attr('cy', d => this.scaleY(d.eigenvalue));

      const pathData = [...Array(numComponents).keys()].map(i => [
        this.scaleX(i + 1),
        this.scaleY(eigenvalues[i]),
      ]);

      const pathDataNull = pathData.map(([x, y]) => [
        x,
        this.scaleY(0.0),
      ]);

      const lineFunc = line();
      const curPath = svg.select('path.line').attr('d');
      const startPath = curPath ? `${curPath}L${curPath.split('L').slice(-1)[0]}` : lineFunc(pathDataNull);
      const endPath = lineFunc(pathData);

      svg.select('path.line')
        .attr('d', startPath)
        .transition()
        .duration(fadeInDuration)
        .attr('d', endPath);
    },
  },

};
</script>
