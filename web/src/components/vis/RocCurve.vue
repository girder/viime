<script>
import * as d3 from 'd3';
import { scaleLinear } from 'd3-scale';
import axios from 'axios';

export default {
  props: {
    rocData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      data: [],
    };
  },
  watch: {
    rocData(newRocdata) {
      d3.select('svg').remove();
      const unformattedData = newRocdata;
      const { sensitivities } = unformattedData;
      const { specificities } = unformattedData;
      const { thresholds } = unformattedData;

      const data = [];

      thresholds.forEach((threshold, i) => {
        data.push({ sensitivity: sensitivities[i], specificity: 1 - specificities[i], threshold });
      });

      const margin = {
        top: 20, right: 60, bottom: 20, left: 80,
      };
      const width = 1200 - margin.left - margin.right;
      const height = 800 - margin.top - margin.bottom;

      const x = d3.scaleLinear()
        .domain([0, 1])
        .range([0, width]);

      const y = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

      const xAxis = d3.axisBottom(x)
        .scale(x);

      const yAxis = d3.axisLeft(x)
        .scale(y);

      const line = d3.line()
        .x((d) => x(d.specificity))
        .y((d) => y(d.sensitivity));

      const svg = d3.select('div#roc').append('svg')
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
        .attr('class', 'x label')
        .attr('text-anchor', 'end')
        .attr('x', width)
        .attr('y', height - 6)
        .text('1 - Specificity');
      svg.append('text')
        .attr('class', 'y label')
        .attr('text-anchor', 'end')
        .attr('y', 6)
        .attr('dy', '.75em')
        .attr('transform', 'rotate(-90)')
        .text('Sensitivity');

      svg.selectAll('path.line').remove();
      svg.append('path')
        .attr('class', 'line')
        .attr('d', line(data));
      const cells = svg.append('g').attr('class', 'vors').selectAll('g');

      const cell = cells.data(data);
      cell.exit().remove();

      const cellEnter = cell.enter().append('g');

      cellEnter.append('circle')
        .attr('class', 'dot')
        .attr('r', 3.5)
        .attr('cx', (d) => x(d.specificity))
        .attr('cy', (d) => y(d.sensitivity));

      cell.select('path').attr('d', (d) => `M${d.vtess.join('L')}Z`);

      cellEnter.append('text').attr('class', 'hidetext')
        .attr('x', (d) => x(d.specificity))
        .attr('y', (d) => y(d.sensitivity))
        .text((d) => `threshold: ${d.threshold}`);
    },
  },
};
</script>

<template>
  <div id="roc" />
</template>

<style>

.line {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
}

.dot {
    fill: none;
}
.vors :hover circle {
  fill: red;
}

.vors :hover text {
	opacity: 1;
}

.hidetext {
    opacity: 0;
}

</style>
