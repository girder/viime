<script lang="ts">
import Vue, { PropType } from 'vue';

export interface BoxData {
  whiskers: {
    d: string;
  }[];
  lines: {
    x1: number;
    x2: number;
    stroke: string;
  }[];
  circles: {
    cx: number;
  }[];
}

export default Vue.extend({
  props: {
    data: {
      type: Object as PropType<BoxData>,
      required: true,
    },
  },
});
</script>

<template>
  <g>
    <g class="whisker">
      <path
        v-for="(w, i) in data.whiskers"
        :key="i"
        fill="none"
        stroke="black"
        opacity="0.7"
        :d="w.d"
      />
    </g>
    <g class="box">
      <line
        v-for="(line, i) in data.lines"
        :key="i"
        v-bind="line"
        stroke-width="16"
        opacity="0.7"
        y1="0"
        y2="0"
      />
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
      />
    </g>
  </g>
</template>
