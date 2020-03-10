<script>
import { select } from 'd3-selection';

import { axisPlot } from './mixins/axisPlot';

export default {
  mixins: [
    axisPlot,
  ],

  props: {
    rows: {
      type: Array, // {pValue: number, log2FoldChange: number, name: string, color?: string}[]
      required: true,
    },
    minFoldChange: {
      type: Number,
      default: 1,
    },
    minLogP: {
      type: Number,
      default: 1,
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
      radius: 3,
      duration: 200,
      xlabel: 'log2(Fold Change)',
      ylabel: '-log10(p-value)',
    };
  },

  computed: {
    transformedRows() {
      return this.rows.map(row => ({
        ...row,
        x: row.log2FoldChange,
        y: -Math.log10(row.pValue),
      }));
    },
    xrange() {
      const max = this.transformedRows.reduce((acc, d) => Math.max(acc, Math.abs(d.x)), 0);
      return [-max, max];
    },
    yrange() {
      const max = this.transformedRows.reduce((acc, d) => Math.max(acc, d.y), 0);
      return [0, max];
    },
  },
  watch: {
    rows() {
      this.update();
    },
    minFoldChange() {
      this.update();
    },
    minLogP() {
      this.update();
    },
  },
  methods: {
    update() {
      //
      // Compute the total variance in all the PCs.
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);

      svg.select('.plot').selectAll('circle')
        .data(this.transformedRows)
        .join((enter) => {
          const r = enter.append('circle');
          r.append('title');
          return r;
        })
        .attr('r', d => (Math.abs(d.x) >= this.minFoldChange && d.y >= this.minLogP ? this.radius * 2 : this.radius))
        .attr('opacity', d => (Math.abs(d.x) >= this.minFoldChange && d.y >= this.minLogP ? 1 : 0.5))
        .attr('cx', d => this.scaleX(d.x))
        .attr('cy', d => this.scaleY(d.y))
        .style('fill', d => d.color)
        .select('title')
        .text(d => `${d.name}: ${d.log2FoldChange} x ${d.pValue}`);
      svg.select('.plot').selectAll('line.x-threshold')
        .data([-1, 1])
        .join('line')
        .attr('class', 'x-threshold')
        .style('stroke', 'black')
        .style('stroke-width', 0.5)
        .attr('x1', d => this.scaleX(d * this.minFoldChange))
        .attr('y1', 0)
        .attr('x2', d => this.scaleX(d * this.minFoldChange))
        .attr('y2', this.height - this.margin.top - this.margin.bottom);
      svg.select('.plot').selectAll('line.y-threshold')
        .data([1])
        .join('line')
        .attr('class', 'y-threshold')
        .style('stroke', 'black')
        .style('stroke-width', 0.5)
        .attr('x1', 0)
        .attr('y1', () => this.scaleY(this.minLogP))
        .attr('x2', this.width - this.margin.left - this.margin.right)
        .attr('y2', () => this.scaleY(this.minLogP));
    },
  },
};
</script>
<template lang="pug">
.main(v-resize:throttle="onResize")
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.plot
    text.x.label(:transform="`translate(${margin.left + dwidth / 2},${height - 10})`")
      | {{xlabel}}
    text.y.label(:transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`")
      | {{ylabel}}
</template>
<style scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}

.plot >>> circle {
  fill: steelblue;
}

.plot >>> circle:hover {
  stroke: black;
}
</style>
