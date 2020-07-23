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
  mounted() {
    // select('svg').remove(); // remove any existing graph

    const margin = {
      top: 40,
      right: 20,
      bottom: 50,
      left: 150,
    };
    const width = 1000 - margin.left - margin.right;
    const height = 800 - margin.top - margin.bottom;

    const x = scaleLinear()
      .domain([0, 1])
      .range([0, width]);

    const y = scaleLinear()
      .domain([0, 1])
      .range([height, 0]);

    const xAxis = axisBottom(x)
      .scale(x);

    const yAxis = axisLeft(x)
      .scale(y);
    const svg = select('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);
    svg.append('g')
      .call(yAxis);
    svg.append('text')
      .attr('text-anchor', 'end')
      .attr('x', width)
      .attr('y', height - 6)
      .text('1 - Specificity');
    svg.append('text')
      .attr('text-anchor', 'end')
      .attr('y', 6)
      .attr('dy', '.75em')
      .attr('transform', 'rotate(-90)')
      .text('Sensitivity');

    const data = this.sensitivities.map((sensitivity, i) => (
      { sensitivity, specificity: 1 - this.specificities[i] }
    ));

    const drawLine = line()
      .x((d) => x(d.specificity))
      .y((d) => y(d.sensitivity));

    // Draw the ROC curve using the data
    svg.selectAll('path.line').remove();
    svg.append('path')
      .attr('class', 'rocCurve')
      .attr('d', drawLine(data));

    // Draw the diagonal line
    svg.append('path')
      .attr('class', 'diagonal')
      .attr('d', drawLine([
        { sensitivity: 0, specificity: 0 },
        { sensitivity: 1, specificity: 1 },
      ]));
  },
};
</script>

<template>
  <div class="rocContainer">
    <span
      style="margin: 10px; font-weight: bold"
      v-text="`AUC = ${auc.toPrecision(3)}`"
    />
    <svg id="svg" />
  </div>
</template>

<style>
.rocContainer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}

.rocCurve {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
}

.diagonal {
  fill: none;
  stroke: black;
  stroke-width: 1.5px;
  stroke-dasharray: 5,5;
}

</style>
