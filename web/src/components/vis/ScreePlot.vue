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
        g.cutoffs
          line.cutoff.cutoff50
          line.cutoff.cutoff80
          line.cutoff.cutoff90
  .tooltip(ref="tooltip")
  span(style="display: none") {{ update }}
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

line.cutoff50 {
  stroke: gray;
}

line.cutoff80 {
  stroke: firebrick;
}

line.cutoff90 {
  stroke: red;
}
</style>

<script>
import { scalePoint } from 'd3-scale';
import { select, event } from 'd3-selection';
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
      validator: prop => !prop || prop.every(v => Number.isFinite(v) && v > 0.0),
    },
    numComponents: {
      default: 10,
      type: Number,
      validator: Number.isInteger,
    },
    showCutoffs: {
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
      xlabel: 'Principal Component',
      ylabel: 'Eigenvalue',
    };
  },

  computed: {
    eigenvaluesInternal() {
      return this.eigenvalues || [];
    },

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
        eigenvaluesInternal,
      } = this;

      return [0.0, Math.max(...eigenvaluesInternal) * 1.1];
    },

    percents() {
      const total = sum(this.eigenvaluesInternal);
      return this.eigenvaluesInternal.map(d => d / total);
    },

    cumulativePercents() {
      const result = [0, ...this.percents];
      for (let i = 1; i < result.length; i += 1) {
        result[i] += result[i - 1];
      }

      return result.slice(1);
    },

    cutoffs() {
      const {
        cumulativePercents,
      } = this;

      const result = [null, null, null];

      for (let i = 0; i < cumulativePercents.length; i += 1) {
        const val = cumulativePercents[i];
        if (val > 0.90) {
          result[2] = i;
          break;
        } else if (val > 0.80 && result[1] === null) {
          result[1] = i;
        } else if (val > 0.50 && result[0] === null) {
          result[0] = i;
        }
      }

      return result;
    },

    update() {
      const {
        eigenvaluesInternal,
        percents,
        cumulativePercents,
        fadeInDuration,
        duration,
        numComponents,
        showCutoffs,
        cutoffs,
      } = this;

      if (this.eigenvaluesInternal.length === 0) {
        return '';
      }

      const radius = 4;

      if (!this.$refs.svg) {
        return '';
      }

      const svg = select(this.$refs.svg);
      const tooltip = select(this.$refs.tooltip);

      const data = eigenvaluesInternal.map((d, i) => ({
        eigenvalue: d,
        percent: percents[i],
        cumPercent: cumulativePercents[i],
      })).slice(0, numComponents);

      const pctFormat = format('.2%');
      const floatFormat = format('.2f');

      // Plot the points.
      this.axisPlot(svg);
      this.setXLabel(this.xlabel);
      this.setYLabel(this.ylabel);

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
              .style('opacity', 0.9);

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
          }))
        .transition()
        .duration(fadeInDuration)
        .attr('r', radius)
        .attr('cx', (d, i) => this.scaleX(i + 1))
        .attr('cy', d => this.scaleY(d.eigenvalue));

      // Plot the line.
      const pathData = [...Array(numComponents).keys()].map(i => [
        this.scaleX(i + 1),
        this.scaleY(eigenvaluesInternal[i]),
      ]);

      const pathDataNull = pathData.map(([x]) => [
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

      // Plot the diagnostic cutoff lines.
      const drawCutoff = (which, where) => {
        const cutoff = svg.select(`line.cutoff${which}`);

        if (where === null || where >= numComponents) {
          cutoff.style('opacity', 0.0);
          return;
        }

        const step = this.scaleX.step();
        const x = this.scaleX(where) + step / 2;

        cutoff.attr('y1', this.scaleY(0))
          .attr('y2', this.scaleY(this.yrange[1]))
          .attr('stroke-dasharray', '10 5 5 5')
          .style('opacity', 1)
          .style('display', showCutoffs ? null : 'none')
          .on('mouseover', () => {
            tooltip.style('left', `${event.clientX + 15}px`)
              .style('top', `${event.clientY - 30}px`)
              .transition()
              .duration(duration)
              .style('opacity', 0.9);

            tooltip.html(`The PCs to the left account for ${which}% of the variance`);
          })
          .on('mouseout', () => {
            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.0);
          })
          .transition()
          .duration(fadeInDuration)
          .attr('x1', x)
          .attr('x2', x);
      };

      drawCutoff('50', cutoffs[0]);
      drawCutoff('80', cutoffs[1]);
      drawCutoff('90', cutoffs[2]);

      return '';
    },
  },

  mounted() {
    this.$forceUpdate();
  },
};
</script>
