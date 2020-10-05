<script lang="ts">
import Vue, { PropType } from 'vue';

export function makeWhiskerLine(start: number, end: number, height: number) {
  return `M${[start, -0.4 * height]}
      l${[0, height * 0.8]}
      m${[0, -0.4 * height]}
      L${[end, 0]}`;
}

export interface BoxData {
  whiskers: {
    start: number;
    end: number;
    height: number;
    text: string;
  }[];
  lines: {
    x1: number;
    x2: number;
    stroke: string;
    text: string;
    height: number;
  }[];
  circles: {
    cx: number;
    value: number;
  }[];
}

export default Vue.extend({
  props: {
    data: {
      type: Object as PropType<BoxData>,
      required: true,
    },
  },
  methods: { makeWhiskerLine },
});
</script>

<template>
  <g>
    <g class="whisker">
      <template
        v-for="(w, i) in data.whiskers"
      >
        <path
          :key="`${i}-path`"
          fill="none"
          stroke="black"
          opacity="0.7"
          :d="makeWhiskerLine(w.start, w.end, w.height)"
        />
        <rect
          :key="`${i}-rect`"
          :x="Math.min(w.start, w.end)"
          :y="w.height * -0.5"
          :width="Math.abs(w.start - w.end)"
          :height="w.height"
          style="fill: transparent"
        >
          <title>{{ w.text }}</title>
        </rect>
      </template>
    </g>
    <g class="box">
      <line
        v-for="(line, i) in data.lines"
        :key="i"
        v-bind="line"
        :stroke-width=".5 * line.height"
        opacity="0.7"
        y1="0"
        y2="0"
      >
        <title>{{ line.text }}</title>
      </line>
    </g>
    <g class="point">
      <circle
        v-for="(circle, i) in data.circles"
        :key="i"
        v-bind="circle"
        class="point outlier"
        fill="black"
        stroke="none"
        opacity="0.7"
        r="2.5"
        cy="0"
      >
        <title>{{ circle.value }}</title>
      </circle>
    </g>
  </g>
</template>
