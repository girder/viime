<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watch, onMounted,
} from '@vue/composition-api';
import { axisTop, axisLeft } from 'd3-axis';
import { select } from 'd3-selection';
import { scaleBand, scaleLinear } from 'd3-scale';
import { boxplotStats } from 'd3-boxplot';
import 'd3-transition';

import { measurementColumnName, measurementValueName } from '@/utils/constants';
import BoxplotBox from '@/components/vis/snippets/BoxplotBox.vue';
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
  values: number[];
}

export default defineComponent({
  props: {
    rows: {
      type: Array as PropType<Row[]>,
      default: () => [],
    },
    groups: {
      type: Array as PropType<Group[]>,
      default: () => [],
    },
  },

  components: { BoxplotBox },

  setup(props, ctx) {
    const svgRef = ref(document.createElement('svg'));
    const mainRef = ref(document.createElement('div'));
    const margin = {
      top: 40,
      right: 20,
      bottom: 50,
      left: 150,
    };
    const xlabel = measurementColumnName;
    const ylabel = measurementValueName;

    const boxHeight = 20;
    // number of groups is len(groups) or 1
    const groupCount = computed(() => (props.groups || []).length || 1);
    const width = ref(800);
    // height is rows * groups per row * height per box (plus margins)
    const height = computed(() => (
      (props.rows.length * boxHeight * groupCount.value)
      + (margin.top + margin.bottom)));

    const {
      dwidth,
      dheight,
      axisPlot,
    } = useAxisPlot(margin, width, height);

    const xrange = computed(() => {
      let min = Number.POSITIVE_INFINITY;
      let max = Number.NEGATIVE_INFINITY;

      function pushValue(v: number) {
        if (v < min) {
          min = v;
        }
        if (v > max) {
          max = v;
        }
      }
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

    const scaleX = computed(() => scaleLinear()
      .domain(xrange.value)
      .range([0, dwidth.value]));
    const scaleY = computed(() => scaleBand()
      // @ts-ignore d3 typings are bad
      .domain(props.rows.map((d) => d.name))
      // @ts-ignore d3 typings are bad
      .range([0, dheight.value], 0.1));
    const scaleGroup = computed(() => scaleBand()
      // @ts-ignore d3 typings are bad
      .domain(props.groups || [])
      // @ts-ignore d3 typings are bad
      .range([0, groupCount.value * boxHeight], 0.1));

    const axisX = computed(() => axisTop(scaleX.value));
    const axisY = computed(() => axisLeft(scaleY.value));

    const boxData = computed(() => {
      const valueStats = props.rows.map((r) => {
        if (r.values) {
          return {
            metabolite: r.name,
            boxes: [{
              title: r.name,
              group: '',
              color: 'black',
              stats: boxplotStats(r.values),
            }],
          };
        }
        if (r.groups) {
          return {
            metabolite: r.name,
            boxes: r.groups.map((g) => ({
              title: `${r.name} ${g.name}`,
              group: g.name,
              color: g.color,
              stats: boxplotStats(g.values),
            })),
          };
        }
        throw new Error('Row must contain 1 of values, groups');
      });

      const _scaleX = scaleX.value;
      const _scaleY = scaleY.value;
      const _scaleGroup = scaleGroup.value;

      return valueStats.map((data) => ({
        metabolite: data.metabolite,
        transform: `translate(0, ${(_scaleY(data.metabolite) || 0) + (boxHeight / 2)})`,
        boxes: data.boxes.map((box) => ({
          title: box.title,
          transform: `translate(0, ${_scaleGroup(box.group) || 0})`,
          lines: box.stats.boxes.map((b) => ({
            x1: _scaleX(b.start),
            x2: _scaleX(b.end),
            stroke: box.color,
          })),
          circles: box.stats.points
            .filter((p) => p.outlier)
            .map((p) => ({
              cx: _scaleX(p.value),
            })),
          whiskers: box.stats.whiskers.map((p) => ({
            d: `
              M${[_scaleX(p.start), -0.4 * boxHeight]}
              l${[0, boxHeight * 0.8]}
              m${[0, -0.4 * boxHeight]}
              L${[_scaleX(p.end), 0]}
            `,
          })),
        })),
      }));
    });

    function update() {
      const svg = select(svgRef.value);
      axisPlot(svg, axisX.value, axisY.value);
    }

    function onResize() {
      const bb = mainRef.value.getBoundingClientRect();
      width.value = bb.width;
    }

    watch(props, () => update());
    onMounted(() => {
      update();
      onResize();
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
      boxData,
      onResize,
    };
  },
});
</script>

<template>
  <div
    ref="mainRef"
    v-resize:throttle="onResize"
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
        <g class="plot">
          <g
            v-for="group in boxData"
            :key="group.metabolite"
            :transform="group.transform"
            class="boxplot"
          >
            <boxplot-box
              v-for="box in group.boxes"
              :key="box.title"
              :transform="box.transform"
              :data="box"
            />
          </g>
        </g>
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
.boxplot {
  transition: .4s ease-in-out;
}
.axes >>> text {
  font-size: 14px;
}
</style>
