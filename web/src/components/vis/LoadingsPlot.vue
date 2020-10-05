<template>
  <div
    ref="mainRef"
    class="main"
  >
    <!-- v-resize:throttle="onResize" -->
    <svg
      ref="svgRef"
      :width="width"
      :height="height"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g class="master">
        <g class="axes" />
        <g class="label x">
          <text>x</text>
        </g>
        <g class="label y">
          <text>y</text>
        </g>
        <g class="crosshairs" />
        <g class="plot" />
      </g>
    </svg>
    <div
      ref="tooltipRef"
      class="tooltip"
    />
  </div>
</template>

<style scoped lang="scss">
g.label {
  opacity: 0;
}
circle {
  fill-opacity: 0.001;
  stroke: black;
}
div.tooltip {
  position: fixed;
  text-align: center;
  padding: 2px;
  background: #eee;
  border: 0px;
  border-radius: 3px;
  pointer-events: none;
  z-index: 20;
  opacity: 1; // 0
}
</style>

<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watchEffect, onMounted,
} from '@vue/composition-api';
import { axisBottom, axisLeft } from 'd3-axis';
import { select, event } from 'd3-selection';
import { format } from 'd3-format';
import { scaleLinear } from 'd3-scale';
import 'd3-transition';

import useAxisPlot from './use/useAxisPlot';

interface Point {
  col: string;
  loadings: number[];
}

// hoisted constants
const margin = {
  top: 20,
  right: 20,
  bottom: 50,
  left: 60,
};
const radius = 4;

const duration = 200;
const fadeInDuration = 500;

function domain(arr: number[]): number[] {
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  arr.forEach((v) => {
    if (v < min) {
      min = v;
    }
    if (v > max) {
      max = v;
    }
  });
  const amax = Math.max(Math.abs(max), Math.abs(min));
  return [-amax, amax];
}

export default defineComponent({
  props: {
    points: {
      required: true,
      type: Array as PropType<Point[]>,
    },
    pcX: {
      type: Number,
      default: 1,
    },
    pcY: {
      type: Number,
      default: 2,
    },
    showCrosshairs: {
      type: Boolean,
      default: true,
    },
  },

  setup(props) {
    const svgRef = ref(document.createElement('svg'));
    const mainRef = ref(document.createElement('div'));
    const tooltipRef = ref(document.createElement('div'));
    const width = ref(400);
    const height = ref(400);

    const {
      dwidth,
      dheight,
      setXLabel,
      setYLabel,
      axisPlot,
    } = useAxisPlot({ margin, width, height });

    const pcXRange = computed(() => {
      const arr = props.points.map((d) => d.loadings[props.pcX - 1]);
      if (arr.length === 0) {
        return [-1, 1];
      }
      return domain(arr);
    });

    const pcYRange = computed(() => {
      const arr = props.points.map((d) => d.loadings[props.pcY - 1]);
      if (arr.length === 0) {
        return [-1, 1];
      }
      return domain(arr);
    });

    const pcRange = computed(() => {
      const x = pcXRange.value;
      const y = pcYRange.value;
      return [Math.min(x[0], y[0]), Math.max(x[1], y[1])];
    });

    const scaleX = computed(() => scaleLinear()
      .domain(pcRange.value)
      .range([0, dwidth.value]));
    const scaleY = computed(() => scaleLinear()
      .domain(pcRange.value)
      .range([dheight.value, 0]));

    const axisX = computed(() => axisBottom(scaleX.value));
    const axisY = computed(() => axisLeft(scaleY.value));

    // call the D3 render function after all refs are mounted
    onMounted(() => watchEffect(() => {
      // Recalculate width/height
      const bb = mainRef.value.getBoundingClientRect();
      height.value = bb.height;
      width.value = bb.width;

      // Set up plot
      const svg = select(svgRef.value);
      axisPlot(svg, axisX.value, axisY.value);
      setXLabel(svg, `PC${props.pcX} correlation`);
      setYLabel(svg, `PC${props.pcY} correlation`);

      // Draw the crosshair
      const crosshair = {
        color: 'gray',
        width: '2px',
      };
      svg
        .select('g.crosshairs')
        .selectAll('line')
        .data([{ x: 10, y: 0 }, { x: 0, y: 10 }])
        .join((enter) => enter.append('line')
          .attr('stroke', crosshair.color)
          .attr('stroke-width', crosshair.width))
        // @ts-ignore d3 typings are bad
        .style('display', props.showCrosshairs ? null : 'none')
        .attr('x1', (d) => scaleX.value(0) - d.x)
        .attr('x2', (d) => scaleX.value(0) + d.x)
        .attr('y1', (d) => scaleY.value(0) - d.y)
        .attr('y2', (d) => scaleY.value(0) + d.y);

      // Draw the scatter plot
      const coordFormat = format('.2f');
      const tooltip = select(tooltipRef.value);
      svg.select('g.plot')
        .selectAll('circle')
        .data(props.points)
        .join((enter) => enter.append('circle')
          .attr('cx', scaleX.value(0))
          .attr('cy', scaleY.value(0))
          .attr('r', 0)
          .style('fill-opacity', 0.001)
          .style('stroke', 'black')
          .on('mouseover', function mouseover(d) {
            select(this)
              .transition()
              .duration(duration)
              .attr('r', 2 * radius);

            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9);
            tooltip.html(`<b>${d.col}</b><br>(${coordFormat(d.loadings[props.pcX - 1])}, ${coordFormat(d.loadings[props.pcY - 1])})`)
              .style('left', `${event.clientX + 15}px`)
              .style('top', `${event.pageY - 30}px`);
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
        .attr('cx', (d) => scaleX.value(d.loadings[props.pcX - 1]))
        .attr('cy', (d) => scaleY.value(d.loadings[props.pcY - 1]));
    }));

    return {
      width,
      height,
      mainRef,
      svgRef,
      tooltipRef,
    };
  },
});
</script>
