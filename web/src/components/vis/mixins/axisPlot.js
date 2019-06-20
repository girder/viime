import { select } from 'd3-selection';
import { scaleLinear, scaleOrdinal } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';

function labelAxis(label, msg, xFunc, yFunc, rot) {
  const text = label.select('text')
    .html(`${msg}`);
  const bbox = text.node().getBBox();
  label.attr('transform', `translate(${xFunc(bbox)},${yFunc(bbox)}) rotate(${rot})`)
    .style('opacity', 1.0);
}

export const axisPlot = {
  methods: {
    axisPlot({margin, xrange, yrange, xlabel, ylabel, duration}) {
      // Collect necessary props.
      const {
        width,
        height,
      } = this.$props;

      // Grab the root SVG element.
      const svg = this.svg = select(this.$refs.svg);

      // Compute the size of the data rectangle.
      const dwidth = width - margin.left - margin.right;
      const dheight = height - margin.top - margin.bottom;

      // Create X and Y scales.
      const scaleX = this.scaleX = scaleLinear()
        .domain(xrange)
        .range([0, dwidth]);
      const scaleY = this.scaleY = scaleLinear()
        .domain(yrange)
        .range([dheight, 0]);

      // Create X and Y axis objects.
      const axisX = this.axisX = axisBottom(scaleX);
      const axisY = this.axisY = axisLeft(scaleY);

      // Set a "master" SVG group.
      const master = svg.select('g.master')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Draw axes.
      const axes = master.select('g.axes');

      this.duration = duration;

      if (axes.select('.x-axis').size() === 0) {
        axes.append('g')
          .classed('x-axis', true)
          .attr('transform', `translate(0,${dheight})`)
          .call(axisX);
      } else {
        axes.select('.x-axis')
          .transition()
          .duration(duration)
          .call(axisX);
      }

      if (axes.select('.y-axis').size() === 0) {
        axes.append('g')
          .classed('y-axis', true)
          .attr('transform', `translate(0,0)`)
          .call(axisY);
      } else {
        axes.select('.y-axis')
          .transition()
          .duration(duration)
          .call(axisY);
      }

      // Label the axes.
      labelAxis(svg.select('.label.x'),
        xlabel,
        bbox => dwidth / 2 - bbox.width / 2,
        bbox => dheight + margin.bottom / 2 + bbox.height / 2,
        0);

      labelAxis(svg.select('.label.y'),
        ylabel,
        bbox => -margin.left / 2 - bbox.height / 2,
        bbox => dheight / 2 + bbox.width / 2,
        -90);
    },
  },
};
