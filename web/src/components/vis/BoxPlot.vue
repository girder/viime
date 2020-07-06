<script lang="ts">
import {
  PropType, defineComponent, computed, ref, watch, onMounted, Ref,
} from '@vue/composition-api';
import { extent } from 'd3-array';
import { axisTop, axisLeft } from 'd3-axis';
import { select } from 'd3-selection';
import { scaleBand, scaleLinear } from 'd3-scale';
import { boxplotStats } from 'd3-boxplot';
import 'd3-transition';
import { flatMapDeep } from 'lodash';

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

// hoisted constants
const margin = {
  top: 40,
  right: 20,
  bottom: 50,
  left: 150,
};
const xlabel = measurementColumnName;
const ylabel = measurementValueName;
const boxHeight = 20;
const toFixed3 = (d: number) => d.toFixed(3);
const count = (values: number[], min: number, max: number) => (
  values.reduce((acc, v) => acc + (v >= min && v < max ? 1 : 0), 0));

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

  setup(props) {
    const svgRef = ref(document.createElement('svg'));
    const mainRef = ref(document.createElement('div'));
    const groupCount = computed(() => (props.groups || []).length || 1);
    const width = ref(800);
    const height = computed(() => (
      (props.rows.length * boxHeight * groupCount.value)
      + (margin.top + margin.bottom)));

    const {
      dwidth,
      dheight,
      axisPlot,
    } = useAxisPlot({
      margin,
      width,
      height,
      topAxis: true,
    });

    const xrange = computed(() => {
      if (props.groups.length) {
        return extent(flatMapDeep(props.rows, (r) => flatMapDeep(r.groups, (g) => g.values)));
      }
      return extent(flatMapDeep(props.rows, (r) => r.values || []));
    }) as Ref<[number, number]>;

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
      const _scaleX = scaleX.value;
      const _scaleY = scaleY.value;
      const _scaleGroup = scaleGroup.value;

      return props.rows.map((r) => {
        let boxes;
        if (r.values) {
          boxes = [{
            title: r.name,
            group: '',
            color: 'black',
            stats: boxplotStats(r.values),
            values: r.values,
          }];
        } else if (r.groups) {
          boxes = r.groups.map((g) => ({
            title: `${r.name} ${g.name}`,
            group: g.name,
            color: g.color,
            stats: boxplotStats(g.values),
            values: g.values,
          }));
        } else {
          throw new Error('Row must contain 1 of values, groups');
        }
        return {
          metabolite: r.name,
          transform: `translate(0, ${(_scaleY(r.name) || 0) + (boxHeight / 2)})`,
          boxes: boxes.map((box) => ({
            title: box.title,
            transform: `translate(0, ${_scaleGroup(box.group) || 0})`,
            lines: [
              {
                x1: _scaleX(box.stats.boxes[0].start),
                x2: _scaleX(box.stats.boxes[0].end) - 0.4,
                stroke: box.color,
                height: boxHeight,
                text: `${r.name}: ${toFixed3(box.stats.fiveNums[1])} (q1) - ${toFixed3(box.stats.fiveNums[2])} (median) = ${count(box.values, box.stats.fiveNums[1], box.stats.fiveNums[2])} Items`,
              }, {
                x1: _scaleX(box.stats.boxes[1].start) + 0.4,
                x2: _scaleX(box.stats.boxes[1].end),
                stroke: box.color,
                height: boxHeight,
                text: `${r.name}: ${toFixed3(box.stats.fiveNums[2])} (median) - ${toFixed3(box.stats.fiveNums[3])} (q3) = ${count(box.values, box.stats.fiveNums[2], box.stats.fiveNums[3])} Items`,
              },
            ],
            circles: box.stats.points
              .filter((p) => p.outlier)
              .map((p) => ({
                cx: _scaleX(p.value),
                value: p.value,
              })),
            whiskers: [
              {
                start: _scaleX(box.stats.whiskers[0].start) || 0,
                end: _scaleX(box.stats.whiskers[0].end) || 0,
                height: boxHeight,
                text: `${r.name}: ${toFixed3(box.stats.whiskers[0].start)} (q1-iqr*1.5) - ${toFixed3(box.stats.fiveNums[1])} (q1) = ${count(box.values, box.stats.whiskers[0].start, box.stats.fiveNums[1])} Items`,
              },
              {
                start: _scaleX(box.stats.whiskers[1].start) || 0,
                end: _scaleX(box.stats.whiskers[1].end) || 0,
                height: boxHeight,
                text: `${r.name}: ${toFixed3(box.stats.fiveNums[3])} (q3) - ${toFixed3(box.stats.whiskers[1].start)} (q3+iqr*1.5) = ${count(box.values, box.stats.fiveNums[3], box.stats.whiskers[1].start)} Items`,
              },
            ],
          })),
        };
      });
    });

    function update() {
      const svg = select(svgRef.value);
      axisPlot(svg, axisX.value, axisY.value);
    }

    function onResize() {
      const bb = mainRef.value.getBoundingClientRect();
      width.value = bb.width;
      update();
    }

    watch(props, () => update());
    onMounted(() => {
      onResize();
      update();
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
    style="overflow-y: auto;"
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
  transition: 0.4s ease-in-out;
}
.axes >>> text {
  font-size: 14px;
}
</style>
