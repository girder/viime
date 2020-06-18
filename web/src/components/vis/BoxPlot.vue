<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watch, onMounted,
} from '@vue/composition-api';
import { axisTop, axisLeft, Axis } from 'd3-axis';
import { select } from 'd3-selection';
import { scaleBand, scaleLinear } from 'd3-scale';
import { boxplot, boxplotStats } from 'd3-boxplot';
import 'd3-transition';

import { measurementColumnName, measurementValueName } from '@/utils/constants';
import useAxisPlot from './use/useAxisPlot';

interface Row {
  name: string;
  values?: number[];
  groups?: {
    name: string;
    color: string;
    values: number[];
  }[];
}

interface Group {
  name: string;
  values?: number[];
}

interface Stats {
  name: string;
  groups: Stats[];
  group: string;
  value: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

export default defineComponent({
  props: {
    rows: {
      type: Array as PropType<Row[]>,
      default: () => [],
    },
    groups: {
      type: Array as PropType<Group[]>,
      required: false,
      default: null,
    },
  },
  setup(props) {
    const svgRef = ref(document.createElement('svg'));
    const margin = {
      top: 20,
      right: 20,
      bottom: 50,
      left: 120,
    };
    const duration = 200;
    const xlabel = measurementColumnName;
    const ylabel = measurementValueName;

    const boxHeight = 25;
    const width = ref(800);
    const height = computed(() => props.rows.length * boxHeight);

    const {
      dwidth,
      dheight,
      axisPlot,
      setXLabel,
      setYLabel,
    } = useAxisPlot<number>(margin, width, height);

    const xrange = computed(() => {
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
      props.rows.forEach((row) => {
        if (row.values) {
          row.values.forEach(pushValue);
        }
        if (row.groups) {
          row.groups.forEach((group) => group.values.forEach(pushValue));
        }
      });
      return [min, max];
    });
    const yrange = [-1, 1];

    const scaleX = computed(() => scaleLinear()
      .domain(xrange.value)
      .range([0, dwidth.value]));
    const scaleY = computed(() => scaleBand()
      .domain(props.rows.map((d) => d.name))
      // @ts-ignore d3 typings are bad
      .range([0, dheight.value], 0.1));
    const scaleGroup = computed(() => scaleBand()
      // @ts-ignore d3 typings are bad
      .domain(props.groups || []));

    const axisX = computed(() => axisTop(scaleX.value) as Axis<number>);
    const axisY = computed(() => axisLeft(scaleY.value) as Axis<number>);

    /**
     * Update function called on mount and whenever
     * props.rows changes
     */
    function update() {
      // Compute the total variance in all the PCs.
      const svg = select<SVGElement, null>(svgRef.value);
      axisPlot(svg, axisX.value, axisY.value);

      // compute stats
      // TODO: formalize shape of stats with interface
      const stats: Stats[] = props.rows.map((d) => ({
        ...d,
        ...(d.values ? boxplotStats(d.values) : {}),
        groups: d.groups ? d.groups.map((group) => ({
          ...group,
          group: group.name,
          name: `${d.name} ${group.name}`,
          ...boxplotStats(group.values),
        })) : null,
      }));

      const layout = boxplot()
        .scale(scaleX.value)
        .vertical(false)
        .showInnerDots(false)
        .bandwidth(boxHeight)
        .boxwidth(boxHeight * 0.8);

      const base = svg.select<SVGGElement>('.plot');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let boxplots: any;

      if (!props.groups) {
        base.selectAll('g.boxplots').remove();
        boxplots = base.selectAll('g.boxplot').data(stats, (d) => d.name)
          .join((enter) => enter.append('g').classed('boxplot', true))
          .attr('transform', (d) => `translate(0, ${scaleY.value(d.name)})`);
      } else {
        base.selectAll('g.boxplot').remove();
        const boxplotGroups = base.selectAll('g.boxplots').data(stats, (d) => d.name)
          .join((enter) => enter.append('g').classed('boxplots', true))
          .attr('transform', (d) => `translate(0, ${scaleY.value(d.name)})`);

        boxplots = boxplotGroups.selectAll('g.group').data((d) => d.groups, (d) => d.group)
          .join((enter) => enter.append('g').classed('group', true))
          .attr('transform', (d) => `translate(0, ${scaleGroup.value(d.group)})`);
      }

      console.log(boxplot(boxplots[0]));

      boxplots
        .transition()
        .duration(duration)
        // @ts-ignore
        .call(layout)
        .end()
        // silently catch any transition interruptions from consecutive updates
        .catch(() => {})
        .then(() => {
          // inject tooltips
          const f = (d: number) => d.toFixed(3);

          // outliers: show the value
          boxplots.select('g.point').selectAll('.outlier')
            .html((d: Stats) => `<title>${f(d.value)}</title>`);

          const count = (values: number[], min: number, max: number) => values
            .reduce((acc, v) => acc + (v >= min && v < max ? 1 : 0), 0);

          // inject rect backgrounds for whiskers
          const whiskers = boxplots.select('.whisker');

          boxplots.select('.whisker path')
            .html((d: Stats) => `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`);
          boxplots.select('.box line')
            .style('stroke', (d) => d.color)
            .html((d: Stats) => `<title>${d.name}: ${f(d.fiveNums[1])} (q1) - ${f(d.fiveNums[2])} (median) = ${count(d.values, d.fiveNums[1], d.fiveNums[2])} Items</title>`);
          boxplots.select('.box line:last-of-type')
            .style('stroke', (d) => d.color)
            .html((d: Stats) => `<title>${d.name}: ${f(d.fiveNums[2])} (median) - ${f(d.fiveNums[3])} (q3) = ${count(d.values, d.fiveNums[2], d.fiveNums[3])} Items</title>`);
          boxplots.select('.whisker path:last-of-type')
            .html((d: Stats) => `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`);

          const bgs = whiskers.selectAll('rect').data((d) => [d, d]).join('rect');
          bgs
            .attr('x', (d: Stats, i: number) => scaleX.value(Math.min(d.whiskers[i].start, d.whiskers[i].end)))
            .attr('y', boxHeight * -0.5)
            .attr('width', (d: Stats, i: number) => scaleX.value(Math.abs(d.whiskers[i].start - d.whiskers[i].end)))
            .attr('height', boxHeight)
            .style('fill', 'transparent')
            .html((d: Stats, i: number) => (i === 0
              ? `<title>${d.name}: ${f(d.whiskers[0].start)} (q1-iqr*1.5) - ${f(d.fiveNums[1])} (q1) = ${count(d.values, d.whiskers[0].start, d.fiveNums[1])} Items</title>`
              : `<title>${d.name}: ${f(d.fiveNums[3])} (q3) - ${f(d.whiskers[1].start)} (q3+iqr*1.5) = ${count(d.values, d.fiveNums[3], d.whiskers[1].start)} Items</title>`));
        });
    }

    watch(props.rows, update);
    onMounted(update);

    return {
      width,
      height,
      margin,
      dwidth,
      dheight,
      xlabel,
      ylabel,
      svgRef,
    };
  },
});
</script>

<template>
  <div class="main">
    <svg
      ref="svgRef"
      :width="width"
      :height="height"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g class="master">
        <g class="axes" />
        <g class="plot" />
      </g>
      <text
        class="x label"
        :transform="`translate(${margin.left + dwidth / 2},${height - 10})`"
      >
        {{ xlabel }}
      </text>
      <text
        class="y label"
        :transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`"
      >
        {{ ylabel }}
      </text>
    </svg>
  </div>
</template>

<style scoped>
.label.x {
  text-anchor: middle;
}

.label.y {
  dominant-baseline: central;
}
</style>
