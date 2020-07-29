<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watchEffect, onMounted, Ref,
} from '@vue/composition-api';
import { axisBottom, axisLeft } from 'd3-axis';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import useAxisPlot from './use/useAxisPlot';

interface Row {
  pValue: number;
  log2FoldChange: number;
  name: string;
  color?: string;
}

interface TransformedRow extends Row {
  x: number;
  y: number;
}

// hoisted constants
const margin = {
  top: 20,
  right: 20,
  bottom: 50,
  left: 50,
};
const radius = 3;
const xlabel = 'log2(Fold Change)';
const ylabel = '-log10(p-value)';

export default defineComponent({
  props: {
    rows: {
      type: Array as PropType<Row[]>,
      default: () => [],
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

  setup(props) {
    const mainRef = ref(document.createElement('div'));

    const width = ref(800);
    const height = computed(() => (
      (props.rows.length * 10)
      + (margin.top + margin.bottom)));

    const {
      dwidth,
      dheight,
      axisPlot,
    } = useAxisPlot({
      margin,
      width,
      height,
      topAxis: false,
    });

    const transformedRows = computed(() => props.rows.map((row) => ({
      ...row,
      x: row.log2FoldChange,
      y: -Math.log10(row.pValue),
    }))) as Ref<TransformedRow[]>;

    const xrange = computed(() => {
      const max = transformedRows.value
        .reduce((acc: number, d: TransformedRow) => Math.max(acc, Math.abs(d.x)), 0);
      return [-max, max];
    }) as Ref<[number, number]>;

    const yrange = computed(() => {
      const max = transformedRows.value
        .reduce((acc: number, d: TransformedRow) => Math.max(acc, d.y), 0);
      return [0, max];
    }) as Ref<[number, number]>;

    const scaleX = computed(() => scaleLinear()
      .domain(xrange.value)
      .range([0, dwidth.value]));

    const scaleY = computed(() => scaleLinear()
      // @ts-ignore d3 typings are bad
      .domain(yrange.value)
      // @ts-ignore d3 typings are bad
      .range([dheight.value, 0]));

    const axisX = computed(() => axisBottom(scaleX.value));
    const axisY = computed(() => axisLeft(scaleY.value));

    function onResize() {
      const bb = mainRef.value.getBoundingClientRect();
      width.value = bb.width;
    }
    onMounted(() => onResize());
    watchEffect(() => {
      const svg = select('svg');
      axisPlot(svg, axisX.value, axisY.value);

      const _scaleX = scaleX.value;
      const _scaleY = scaleY.value;

      // @ts-ignore
      svg.select('.plot').selectAll('circle')
        .data(transformedRows.value)
        .join((enter) => {
          const r = enter.append('circle');
          r.append('title');
          return r;
        })
        // @ts-ignore
        .attr('r', (d) => (Math.abs(d.x) >= props.minFoldChange && d.y >= props.minLogP ? radius * 2 : radius))
        // @ts-ignore
        .attr('opacity', (d) => (Math.abs(d.x) >= props.minFoldChange && d.y >= props.minLogP ? 1 : 0.5))
        // @ts-ignore
        .attr('cx', (d) => _scaleX(d.x))
        // @ts-ignore
        .attr('cy', (d) => _scaleY(d.y))
        // @ts-ignore
        .style('fill', (d) => d.color)
        .select('title')
        // @ts-ignore
        .text((d) => `${d.name}: ${d.log2FoldChange} x ${d.pValue}`);
      svg.select('.plot').selectAll('line.x-threshold')
        .data([-1, 1])
        .join('line')
        .attr('class', 'x-threshold')
        .style('stroke', 'black')
        .style('stroke-width', 0.5)
        // @ts-ignore
        .attr('x1', (d) => _scaleX(d * props.minFoldChange))
        .attr('y1', 0)
        // @ts-ignore
        .attr('x2', (d) => _scaleX(d * props.minFoldChange))
        // @ts-ignore
        .attr('y2', height.value - margin.top - margin.bottom);

      svg.select('.plot').selectAll('line.y-threshold')
        .data([1])
        .join('line')
        .attr('class', 'y-threshold')
        .style('stroke', 'black')
        .style('stroke-width', 0.5)
        .attr('x1', 0)
        // @ts-ignore
        .attr('y1', () => _scaleY(props.minLogP))
        // @ts-ignore
        .attr('x2', width.value - margin.left - margin.right)
        // @ts-ignore
        .attr('y2', () => _scaleY(props.minLogP));
    });

    return {
      width,
      height,
      margin,
      dwidth,
      dheight,
      xlabel,
      ylabel,
      mainRef,
      onResize,
    };
  },
});

</script>
<template>
  <div
    id="mainRef"
    ref="mainRef"
    v-resize:throttle="onResize"
    class="main"
  >
    <svg
      ref="svg"
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
      >{{ xlabel }}</text>
      <text
        class="y label"
        :transform="`translate(${10},${margin.top + dheight / 2})rotate(-90)`"
      >{{ ylabel }}</text>
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

.plot >>> circle {
  fill: steelblue;
}

.plot >>> circle:hover {
  stroke: black;
}
</style>
