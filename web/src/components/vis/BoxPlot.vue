<script>
import { select } from 'd3-selection';
import { scaleBand } from 'd3-scale';
import { boxplot, boxplotStats } from 'd3-boxplot';
import 'd3-transition';

import { axisPlot } from './mixins/axisPlot';
import { measurementColumnName, measurementValueName } from '../../utils/constants';


export default {
  mixins: [
    axisPlot,
  ],
  props: {
    rows: { // {name: string, values?: number[],
      //  groups?: {name: string, color: string, values: number[][]}
      // }[]
      type: Array,
      default: () => [],
    },
    groups: {
      type: Array,
      required: false,
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
      ylabel: measurementColumnName,
      xlabel: measurementValueName,
    };
  },
  computed: {
    scaleY() {
      const { rows, dheight } = this;
      return scaleBand()
        .domain(rows.map(d => d.name))
        .range([0, dheight], 0.1);
    },
    scaleGroup() {
      return scaleBand()
        .domain(this.groups)
        .range([0, this.scaleY.bandwidth()], 0.1);
    },
    xrange() {
      let min = Number.POSITIVE_INFINITY;
      let max = Number.NEGATIVE_INFINITY;

      const pushValue = (v) => {
        if (v < min) {
          min = v;
        }
        if (v > max) {
          max = v;
        }
      };
      this.rows.forEach((row) => {
        if (row.values) {
          row.values.forEach(pushValue);
        }
        if (row.groups) {
          row.groups.forEach(group => group.values.forEach(pushValue));
        }
      });
      return [min, max];
    },
    boxHeight() {
      return this.groups.length === 0 ? this.scaleY.bandwidth() : this.scaleGroup.bandwidth();
    },
  },

  methods: {
    update() {
      //
      // Compute the total variance in all the PCs.
      const svg = select(this.$refs.svg);
      this.axisPlot(svg);

      // compute stats
      const stats = this.rows.map(d => ({
        ...d,
        ...(d.values ? boxplotStats(d.values) : {}),
        groups: d.groups ? d.groups.map(group => ({
          ...group,
          group: group.name,
          name: `${d.name} ${group.name}`,
          ...boxplotStats(group.values),
        })) : null,
      }));

      const layout = boxplot()
        .scale(this.scaleX)
        .vertical(false)
        .showInnerDots(false)
        .bandwidth(this.boxHeight)
        .boxwidth(this.boxHeight * 0.8);

      const base = svg.select('.plot');
      let boxplots;

      if (this.groups.length === 0) {
        base.selectAll('g.boxplots').remove();
        boxplots = base.selectAll('g.boxplot').data(stats, d => d.name)
          .join(enter => enter.append('g').classed('boxplot', true))
          .attr('transform', d => `translate(0, ${this.scaleY(d.name)})`);
      } else {
        base.selectAll('g.boxplot').remove();
        const boxplotGroups = base.selectAll('g.boxplots').data(stats, d => d.name)
          .join(enter => enter.append('g').classed('boxplots', true))
          .attr('transform', d => `translate(0, ${this.scaleY(d.name)})`);

        boxplots = boxplotGroups.selectAll('g.group').data(d => d.groups, d => d.group)
          .join(enter => enter.append('g').classed('group', true))
          .attr('transform', d => `translate(0, ${this.scaleGroup(d.group)})`);
      }

      const finished = boxplots
        .transition()
        .duration(this.duration)
        .each(function update(...args) {
          // call separately since boxplot doesn't handle the phases properly
          layout.call(this, select(this), ...args);
        })
        .end();

      finished.then(() => {
        // inject tooltips

        const f = d => d.toFixed(3);

        // outliers: show the value
        boxplots.select('g.point').selectAll('.outlier')
          .html(d => `<title>${f(d.value)}</title>`);

        const count = (values, min, max) => values
          .reduce((acc, v) => acc + (v >= min && v < max ? 1 : 0), 0);

        // inject rect backgrounds for whiskers
        const whisers = boxplots.select('.whisker');

        boxplots.select('.whisker path')
          .html(d => `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`);
        boxplots.select('.box line')
          .style('stroke', d => d.color)
          .html(d => `<title>${d.name}: ${f(d.fiveNums[1])} (q1) - ${f(d.fiveNums[2])} (median) = ${count(d.values, d.fiveNums[1], d.fiveNums[2])} Items</title>`);
        boxplots.select('.box line:last-of-type')
          .style('stroke', d => d.color)
          .html(d => `<title>${d.name}: ${f(d.fiveNums[2])} (median) - ${f(d.fiveNums[3])} (q3) = ${count(d.values, d.fiveNums[2], d.fiveNums[3])} Items</title>`);
        boxplots.select('.whisker path:last-of-type')
          .html(d => `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`);

        const bgs = whisers.selectAll('rect').data(d => [d, d]).join('rect');
        bgs
          .attr('x', (d, i) => this.scaleX(Math.min(d.whiskers[i].start, d.whiskers[i].end)))
          .attr('y', this.boxHeight * -0.5)
          .attr('width', (d, i) => this.scaleX(Math.abs(d.whiskers[i].start - d.whiskers[i].end)))
          .attr('height', this.boxHeight)
          .style('fill', 'transparent')
          .html((d, i) => (i === 0
            ? `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`
            : `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`));
      });
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

<style scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}
</style>
