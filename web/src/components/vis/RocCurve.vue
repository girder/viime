<script>
import { scaleLinear } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import { line } from 'd3-shape';
import { select } from 'd3-selection';

export default {
  props: {
    sensitivities: {
      type: Array,
      required: true,
    },
    specificities: {
      type: Array,
      required: true,
    },
    auc: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      margin: {
        top: 30,
        right: 20,
        bottom: 50,
        left: 150,
      },
    };
  },
  computed: {
    width() {
      return 1000 - this.margin.left - this.margin.right;
    },
    height() {
      return 850 - this.margin.top - this.margin.bottom;
    },
    xScale() {
      return scaleLinear()
        .domain([0, 1])
        .range([0, this.width]);
    },
    yScale() {
      return scaleLinear()
        .domain([0, 1])
        .range([this.height, 0]);
    },
    drawLine() {
      return line()
        .x((d) => this.xScale(d.specificity))
        .y((d) => this.yScale(d.sensitivity));
    },
    curvePlotData() {
      return this.sensitivities.map((sensitivity, i) => (
        { sensitivity, specificity: 1 - this.specificities[i] }
      ));
    },
  },
  mounted() {
    // draw plot axes
    const xAxis = axisBottom(this.xScale)
      .scale(this.xScale);
    const yAxis = axisLeft(this.xScale)
      .scale(this.yScale);
    select('g#xAxis')
      .call(xAxis);
    select('g#yAxis')
      .call(yAxis);
  },
};
</script>

<template>
  <div class="rocContainer">
    <svg
      :width="width + margin.left + margin.right"
      :height="height + margin.top + margin.bottom"
    >
      <g :transform="`translate(${margin.left},${margin.top})`">
        <g
          id="xAxis"
          :transform="`translate(0,${height})`"
        />
        <g id="yAxis" />
        <g>
          <path
            class="rocCurve"
            :d="drawLine(curvePlotData)"
          />
          <path
            class="diagonal"
            :d="drawLine([
              { sensitivity: 0, specificity: 0 },
              { sensitivity: 1, specificity: 1 },
            ])"
          />
        </g>
        <text
          text-anchor="end"
          class="label"
          :y="height - 6"
          :x="width"
        >1 - Specificity</text>
        <text
          text-anchor="end"
          class="label"
          y="6"
          dy=".75em"
          transform="rotate(-90)"
        >Sensitivity</text>
      </g>
      <g :transform="`translate(${width / 2},${margin.top - 10})`">
        <text
          class="auc-label"
          v-text="`Area Under the Curve (AUC) = ${auc.toPrecision(3)}`"
        />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.rocContainer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}

.auc-label {
  font-size: 1.1em;
  font-weight: bold;
}

.rocCurve {
  fill: none;
  stroke: steelblue;
  stroke-width: 3px;
}

.diagonal {
  fill: none;
  stroke: black;
  stroke-width: 3px;
  stroke-dasharray: 5,5;
}

g {
  font-size: 1.2em;
  stroke-width: 3px;
}

.label {
  font-size: 1.5em;
}

</style>
