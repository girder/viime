<script>
import { scaleLinear } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import { line } from 'd3-shape';
import { select } from 'd3-selection';

export default {
  props: {
    rocData: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    select('svg').remove(); // remove any existing graph

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

    const graphLine = line()
      .x((d) => x(d.specificity))
      .y((d) => y(d.sensitivity));

    const svg = select('div#roc').append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    svg.append('g')
      .attr('class', 'axis')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);
    svg.append('g')
      .attr('class', 'axis')
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

    //
    const { sensitivities } = this.rocData;
    const { specificities } = this.rocData;

    const data = [];

    // Get the data to be plotted
    sensitivities.forEach((sensitivity, i) => {
      data.push({ sensitivity, specificity: 1 - specificities[i] });
    });

    // Draw the ROC curve using the data
    svg.selectAll('path.line').remove();
    svg.append('path')
      .attr('class', 'line')
      .attr('d', graphLine(data));
  },
};
</script>

<template>
  <div>
    <span v-text="`AUC = ${rocData.auc}`" />
    <div id="roc" />
  </div>
</template>

<style>

.line {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
}

</style>
