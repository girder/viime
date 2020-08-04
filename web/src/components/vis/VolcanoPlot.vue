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

  setup(props) {
    const svgRef = ref() as Ref<HTMLElement>;
    const mainRef = ref() as Ref<HTMLElement>;

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
      .domain(yrange.value)
      .range([dheight.value, 0]));

    const axisX = computed(() => axisBottom(scaleX.value));
    const axisY = computed(() => axisLeft(scaleY.value));

    onMounted(() => {
      watchEffect(() => {
        // reactive dependencies
        const mainRefVal = mainRef.value;
        const svgRefVal = svgRef.value;
        const transformedRowsVal = transformedRows.value;
        const minFoldChangeProp = props.minFoldChange;
        const minLogPProp = props.minLogP;
        const axisXVal = axisX.value;
        const axisYVal = axisY.value;
        const scaleXVal = scaleX.value;
        const scaleYVal = scaleY.value;
        const widthVal = width.value;
        const heightVal = height.value;

        // Recalculate width/height
        const bb = mainRefVal.getBoundingClientRect();
        width.value = bb.width;

        const svg = select(svgRefVal);
        axisPlot(svg, axisXVal, axisYVal);

        // @ts-ignore d3 types cause issues
        svg.select('.plot').selectAll('circle')
          .data<TransformedRow>(transformedRowsVal)
          .join((enter) => {
            const r = enter.append('circle');
            r.append('title');
            return r;
          })
          .attr('r', (d) => (Math.abs(d.x) >= minFoldChangeProp && d.y >= minLogPProp ? radius * 2 : radius))
          .attr('opacity', (d) => (Math.abs(d.x) >= minFoldChangeProp && d.y >= minLogPProp ? 1 : 0.5))
          .attr('cx', (d) => scaleXVal(d.x))
          .attr('cy', (d) => scaleYVal(d.y))
          .style('fill', (d) => d.color)
          .select('title')
          .text((d) => `${d.name}: ${d.log2FoldChange} x ${d.pValue}`);
        svg.select('.plot').selectAll('line.x-threshold')
          .data([-1, 1])
          .join('line')
          .attr('class', 'x-threshold')
          .style('stroke', 'black')
          .style('stroke-width', 0.5)
          .attr('x1', (d) => scaleXVal(d * minFoldChangeProp))
          .attr('y1', 0)
          .attr('x2', (d) => scaleXVal(d * minFoldChangeProp))
          .attr('y2', heightVal - margin.top - margin.bottom);

        svg.select('.plot').selectAll('line.y-threshold')
          .data([1])
          .join('line')
          .attr('class', 'y-threshold')
          .style('stroke', 'black')
          .style('stroke-width', 0.5)
          .attr('x1', 0)
          .attr('y1', scaleYVal(minLogPProp))
          .attr('x2', widthVal - margin.left - margin.right)
          .attr('y2', scaleYVal(minLogPProp));
      });
    });

    return {
      width,
      height,
      margin,
      dwidth,
      dheight,
      xlabel,
      ylabel,
      svgRef,
      mainRef,
    };
  },
});

</script>
<template>
  <div
    ref="mainRef"
    class="main"
  >
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
