<script>
import * as d3 from 'd3';

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
  mounted() {
    d3.select('svg').remove();
    const unformattedData = this.rocData;
    const { sensitivities } = unformattedData;
    const { specificities } = unformattedData;

    const data = [];

    sensitivities.forEach((sensitivity, i) => {
      data.push({ sensitivity: sensitivity, specificity: 1 - specificities[i] });
    });

    const margin = {
      top: 20, right: 65, bottom: 20, left: 80,
    };
    const width = 1000 - margin.left - margin.right;
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

    // const area = d3.area()
    //   .x((d) => x(d.specificity))
    //   .y0(height)
    //   .y1((d) => y(d.sensitivity));

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
      // .attr('text-anchor', 'end')
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
    // svg.selectAll('path.area').remove();

    svg.append('path')
      .attr('class', 'line')
      .attr('d', line(data));

    // svg.append("path")
    //   .datum(data)
    //   .attr('class', 'area')
    //   .attr("d", area)

  },
  computed: {
    // extremely inaccurate numerical AUC
    // auc() {
    //   if (!this.rocData.specificities) {
    //     return 0;
    //   }
    //   const n = this.rocData.specificities.length;
    //   const deltaX = 1 / n;
    //   let sum = 0;
    //   // let x;
    //   let y;
    //   for (let i = 0; i < n; i += 1) {
    //     // x = this.rocData.specificities[i] * deltaX;
    //     y = this.rocData.sensitivities[i];
    //     if (i === 0) {
    //       sum += y;
    //     } else if (i % 2 === 1) {
    //       sum += (4 * y);
    //     } else {
    //       sum += (2 * y);
    //     }
    //   }
    //   return (deltaX / 3) * sum;
    // },
  },
};
</script>

<template>
  <div>
    <!-- <span v-text="`AUC = ${auc}`" /> -->
    <div id="roc" />
  </div>
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

.area {
  fill: lightblue;
}
</style>
