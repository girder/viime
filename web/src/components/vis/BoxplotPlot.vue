<script>
import { select } from 'd3-selection';
import { scaleBand } from 'd3-scale';
import { boxplot, boxplotStats } from 'd3-boxplot';
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
    rows: { // {name: string, values: number[]}[]
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      margin: {
        top: 20,
        right: 20,
        bottom: 50,
        left: 120,
      },
      duration: 200,
      ylabel: 'Metabolite',
      xlabel: 'Measurement',
      initialRun: false,
    };
  },
  computed: {
    reactiveUpdate() {
      if (!this.initialRun) {
        return '';
      }
      this.update();
      return Math.random().toString();
    },
    scaleY() {
      const { rows, dheight } = this;
      return scaleBand()
        .domain(rows.map(d => d.name))
        .range([0, dheight], 0.1);
    },
    xrange() {
      let min = Number.POSITIVE_INFINITY;
      let max = Number.NEGATIVE_INFINITY;
      this.rows.forEach((row) => {
        row.values.forEach((v) => {
          if (v < min) {
            min = v;
          }
          if (v > max) {
            max = v;
          }
        });
      });
      return [min, max];
    },
  },

  mounted() {
    this.initialRun = true;
  },

  methods: {
    update() {
      if (!this.$refs.svg) {
        return;
      }
      //
      // Compute the total variance in all the PCs.
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);

      // Draw the data.

      const layout = boxplot()
        .scale(this.scaleX)
        .vertical(false)
        .bandwidth(this.scaleY.bandwidth())
        .boxwidth(this.scaleY.bandwidth() * 0.8)
        .showInnerDots(false);

      const stats = this.rows.map(d => Object.assign({}, d, boxplotStats(d.values)));
      svg.select('.plot').selectAll('g.boxplot').data(stats)
        .join(enter => enter.append('g').classed('boxplot', true))
        .attr('transform', d => `translate(0, ${this.scaleY(d.name)})`)
        .transition()
        .duration(this.duration)
        .call(layout);
    },
  },
};
</script>

<template lang="pug">
div
  svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.master
      g.axes
      g.plot
    text.x.label(:transform="`translate(${margin.left + dwidth / 2},${height - 10})`")
      | {{xlabel}}
    text.y.label(:transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`")
      | {{ylabel}}

  span(style="display: none") {{ reactiveUpdate }}
</template>

<style scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}
</style>
