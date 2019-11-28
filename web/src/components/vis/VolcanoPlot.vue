<script>
import { scalePoint } from 'd3-scale';
import { select, event } from 'd3-selection';
import { format } from 'd3-format';
import { line } from 'd3-shape';
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';

export default {
  mixins: [
    axisPlot,
  ],

  props: {
    rows: {
      type: Array, //{pValue: number, foldChange: number, name: string}[]
      required: true
    }
  },

  data() {
    return {
      margin: {
        top: 20,
        right: 20,
        bottom: 50,
        left: 50,
      },
      radius: 4,
      duration: 200,
      xlabel: 'log2(Fold Change)',
      ylabel: '-log10(p-value)',
    };
  },

  computed: {
    transformedRows() {
      return this.rows.map(row => ({
        ...row,
        x: Math.log2(row.foldChange),
        y: -Math.log10(row.pValue)
      }));
    },
    xrange() {
      const max = this.transformedRows.reduce((acc, d) => Math.max(acc, Math.abs(d.x)), 0);
      return [-max, max];
    },
    yrange() {
      const max = this.transformedRows.reduce((acc, d) => Math.max(acc, d.y), 0);
      return [0, max];
    }
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
          r.attr('r', this.radius);
          r.append('title');
          return r;
        })
        .attr('cx', d => this.scaleX(d.x))
        .attr('cy', d => this.scaleY(d.y))
        .select('title').text(d => `${d.name}: ${d.foldChange} x ${d.pValue}`);
    },
  },
};
</script>
<template lang="pug">
.main(v-resize:throttle="onResize")
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveUpdate")
    g.master
      g.axes
      g.plot
    text.x.label(:transform="`translate(${margin.left + dwidth / 2},${height - 10})`")
      | {{xlabel}}
    text.y.label(:transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`")
      | {{ylabel}}
</template>
<style lang="scss" scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}

circle {
  stroke: black;
  fill: white;
}
</style>
