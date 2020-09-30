<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watchEffect, onMounted, Ref,
} from '@vue/composition-api';
import { axisBottom, axisLeft } from 'd3-axis';
import { scaleBand, scaleLinear } from 'd3-scale';
import { select, event } from 'd3-selection';
import 'd3-transition';

import useAxisPlot from './use/useAxisPlot';

const margin = {
  top: 20, right: 20, bottom: 100, left: 50,
};
const fadeInDuration = 500;
const duration = 200;
const maxLabelLength = 15;

interface VipValue {
  col: string;
  vip: number;
}

export default defineComponent({
  props: {
    vipScores: {
      required: true,
      type: Array as PropType<VipValue[]>,
    },
    sortVip: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  setup(props) {
    const svgRef = ref() as Ref<HTMLElement>;
    const mainRef = ref() as Ref<HTMLElement>;
    const tooltipRef = ref() as Ref<HTMLElement>;
    const width = ref(400);
    const height = ref(400);

    const {
      dwidth,
      dheight,
      setXLabel,
      setYLabel,
      axisPlot,
    } = useAxisPlot({ margin, width, height });

    const labels = computed(() => props.vipScores.map((v) => v.col));
    const vipScores = computed(() => props.vipScores.map((v) => v.vip));

    const scaleX = computed(() => scaleBand<string>()
      .domain(labels.value)
      .range([0, dwidth.value])
      .padding(0.4));
    const yRange = computed(() => [0.0, Math.max(...vipScores.value) * 1.1]);
    const scaleY = computed(() => scaleLinear()
      .domain(yRange.value)
      .range([dheight.value, 0]));

    const axisX = computed(() => axisBottom(scaleX.value)
      .tickFormat((tick) => {
        if (tick.length > maxLabelLength) {
          return `${tick.substring(0, maxLabelLength - 3)}...`;
        }
        return tick;
      }));
    const axisY = computed(() => axisLeft(scaleY.value));

    onMounted(() => {
      watchEffect(() => {
        // Recalculate width/height
        const bb = mainRef.value.getBoundingClientRect();
        height.value = bb.height;
        width.value = bb.width;

        // Set up plot
        const svg = select(svgRef.value);
        const tooltip = select(tooltipRef.value);
        axisPlot(svg, axisX.value, axisY.value);
        setXLabel(svg, 'Component');
        setYLabel(svg, 'VIP Score');

        // @ts-ignore d3 typings are bad
        svg.select('g.bars')
          .selectAll('rect')
          .data(props.vipScores)
          // @ts-ignore d3 typings are bad
          .join((enter) => enter.append('rect')
            .attr('x', (d) => scaleX.value(d.col))
            .attr('y', (d) => scaleY.value(d.vip))
            .attr('width', scaleX.value.bandwidth())
            .attr('height', (d) => dheight.value - scaleY.value(d.vip))
            .style('fill', 'black')
            .style('fill-opacity', 1.0)
            .on('mouseover', (d) => {
              tooltip.transition()
                .duration(duration)
                .style('opacity', 0.9);
              tooltip.html(`<b>${d.col}</b><br>${d.vip}`)
                .style('left', `${event.clientX + 15}px`)
                .style('top', `${event.pageY - 30}px`);
            })
            .on('mouseout', () => {
              tooltip.transition()
                .duration(duration)
                .style('opacity', 0.0);
            }))
          .transition()
          .duration(fadeInDuration)
          .attr('x', (d) => scaleX.value(d.col))
          .attr('y', (d) => scaleY.value(d.vip))
          .attr('height', (d) => dheight.value - scaleY.value(d.vip));

        svg.select('g.label.x')
          .selectAll('text')
          .attr('dy', 30);
        svg.select('g.x-axis')
          .selectAll('text')
          .attr('dx', -40)
          .attr('dy', -7)
          .attr('transform', 'rotate(-90)')
          .on('mouseover', (d) => {
            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.9);
            tooltip.html(`<b>${d}</b>`)
              .style('left', `${event.clientX + 15}px`)
              .style('top', `${event.pageY - 30}px`);
          })
          .on('mouseout', () => {
            tooltip.transition()
              .duration(duration)
              .style('opacity', 0.0);
          });
      });
    });

    return {
      svgRef,
      mainRef,
      tooltipRef,
      width,
      height,
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
        <g class="axes">
          <g class="label x">
            <text />
          </g>
          <g class="label y">
            <text />
          </g>
        </g>
        <g class="plot">
          <g class="bars" />
        </g>
      </g>
    </svg>
    <div
      ref="tooltipRef"
      class="tooltip"
    />
  </div>
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
