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
          <path class="line" />
          <g class="points" />
          <g class="cutoffs">
            <line class="cutoff cutoff50" />
            <line class="cutoff cutoff80" />
            <line class="cutoff cutoff90" />
          </g>
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

<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watchEffect, onMounted, Ref,
} from '@vue/composition-api';
import { axisBottom, axisLeft } from 'd3-axis';
import { scalePoint, scaleLinear } from 'd3-scale';
import { select, event } from 'd3-selection';
import { format } from 'd3-format';
import { line } from 'd3-shape';
import 'd3-transition';

import useAxisPlot from './use/useAxisPlot';

const sum = (arr: number[]) => arr.reduce((acc, x) => acc + x, 0);

const radius = 4;
const margin = {
  top: 20, right: 20, bottom: 50, left: 50,
};
const fadeInDuration = 500;
const duration = 200;

export default defineComponent({
  props: {
    eigenvalues: {
      required: true,
      type: Array as PropType<number[]>,
      validator: (prop: number[]) => prop.every((v) => Number.isFinite(v) && v > 0.0),
    },
    numComponents: {
      type: Number,
      default: 10,
    },
    showCutoffs: {
      type: Boolean,
      default: true,
    },
  },

  setup(props) {
    const svgRef = ref() as Ref<HTMLElement>;
    const mainRef = ref() as Ref<HTMLElement>;
    const tooltipRef = ref() as Ref<HTMLElement>;
    const width = ref(400);
    const height = ref(400);

    const numRendered = computed(() => Math.min(props.numComponents, props.eigenvalues.length));

    const {
      dwidth,
      dheight,
      setXLabel,
      setYLabel,
      axisPlot,
    } = useAxisPlot({ margin, width, height });

    const scaleX = computed(() => {
      const labels = [...Array(numRendered.value).keys()].map((d) => d + 1);
      return scalePoint<number>()
        .domain(labels)
        .range([0, dwidth.value]);
    });
    const yRange = computed(() => [0.0, Math.max(...props.eigenvalues) * 1.1]);
    const scaleY = computed(() => scaleLinear()
      .domain(yRange.value)
      .range([dheight.value, 0]));

    const axisX = computed(() => axisBottom(scaleX.value));
    const axisY = computed(() => axisLeft(scaleY.value));

    const percents = computed(() => {
      const total = sum(props.eigenvalues);
      return props.eigenvalues.map((d) => d / total);
    });

    const cumulativePercents = computed(() => {
      const result = [0, ...percents.value];
      for (let i = 1; i < result.length; i += 1) {
        result[i] += result[i - 1];
      }
      return result.slice(1);
    });

    const cutoffs = computed(() => {
      const result: (number | null)[] = [null, null, null];
      for (let i = 0; i < cumulativePercents.value.length; i += 1) {
        const val = cumulativePercents.value[i];
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
    });

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
        setXLabel(svg, 'Principal Component');
        setYLabel(svg, 'Eigenvalue');

        if (props.eigenvalues.length === 0) {
          return;
        }

        const data = props.eigenvalues.map((d, i) => ({
          eigenvalue: d,
          percent: percents.value[i],
          cumPercent: cumulativePercents.value[i],
        })).slice(0, numRendered.value);

        const pctFormat = format('.2%');
        const floatFormat = format('.2f');

        svg.select('g.points')
          .selectAll('circle')
          .data(data)
          .join((enter) => enter.append('circle')
            .attr('cx', (d, i) => scaleX.value(i + 1) as number)
            .attr('cy', scaleY.value(0))
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
          .attr('cx', (d, i) => scaleX.value(i + 1) as number)
          .attr('cy', (d) => scaleY.value(d.eigenvalue));

        // Plot the line.
        const pathData: [number, number][] = [...Array(numRendered.value).keys()]
          .map((i) => [
            scaleX.value(i + 1) as number,
            scaleY.value(props.eigenvalues[i]),
          ]);

        const pathDataNull: [number, number][] = pathData.map(([x]) => [
          x,
          scaleY.value(0.0),
        ]);

        const lineFunc = line();
        const curPath = svg.select('path.line').attr('d');
        const startPath = curPath || lineFunc(pathDataNull);
        const endPath = lineFunc(pathData);
        svg.select('path.line')
          // @ts-ignore d3 typings are bad
          .attr('d', startPath)
          .transition()
          .duration(fadeInDuration)
          // @ts-ignore d3 typings are bad
          .attr('d', endPath);

        // Plot the diagnostic cutoff lines.
        const drawCutoff = (which: string, where: number | null) => {
          const cutoff = svg.select(`line.cutoff${which}`);

          if (where === null || where === 0 || where >= numRendered.value) {
            cutoff.style('opacity', 0.0);
            return;
          }

          const step = scaleX.value.step();
          const x = scaleX.value(where) as number + step / 2;

          cutoff.attr('y1', scaleY.value(yRange.value[0]))
            .attr('y2', scaleY.value(yRange.value[1]))
            .attr('stroke-dasharray', '10 5 5 5')
            .style('opacity', 1)
            // @ts-ignore d3 typings are bad
            .style('display', props.showCutoffs ? null : 'none')
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

        drawCutoff('50', cutoffs.value[0]);
        drawCutoff('80', cutoffs.value[1]);
        drawCutoff('90', cutoffs.value[2]);
      });
    });

    return {
      svgRef,
      mainRef,
      tooltipRef,
      width,
      height,
      numRendered,
      scaleX,
      yRange,
      scaleY,
      axisX,
      axisY,
      percents,
      cumulativePercents,
      cutoffs,
    };
  },
});
</script>
