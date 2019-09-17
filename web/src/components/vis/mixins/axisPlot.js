import { scaleLinear } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';

function labelAxis(label, msg, xFunc, yFunc, rot) {
  const text = label.select('text')
    .html(`${msg}`);
  const bbox = text.node().getBBox();
  label.attr('transform', `translate(${xFunc(bbox)},${yFunc(bbox)}) rotate(${rot})`)
    .style('opacity', 1.0);
}

export const axisPlot = {
  props: {
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      axisPlotInitialized: false,
      margin: {
        top: null,
        right: null,
        bottom: null,
        left: null,
      },
      xrange: [-1, 1],
      yrange: [-1, 1],
      duration: 500,
      svg: null,
    };
  },
  computed: {
    dwidth() {
      const { width, margin } = this;
      return width - margin.left - margin.right;
    },
    dheight() {
      const { height, margin } = this;
      return height - margin.top - margin.bottom;
    },
    scaleX() {
      const { xrange, dwidth } = this;
      return scaleLinear()
        .domain(xrange)
        .range([0, dwidth]);
    },
    scaleY() {
      const { yrange, dheight } = this;
      return scaleLinear()
        .domain(yrange)
        .range([dheight, 0]);
    },
    axisX() {
      return axisBottom(this.scaleX);
    },
    axisY() {
      return axisLeft(this.scaleY);
    },

  },
  methods: {
    axisPlot(svg) {
      const {
        margin,
        dheight,
        axisX,
        duration,
        axisY,
      } = this;

      this.svg = svg;

      // Set a "master" SVG group.
      const master = svg.select('g.master')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // Draw axes.
      const axes = master.select('g.axes');

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
          .attr('transform', 'translate(0,0)')
          .call(axisY);
      } else {
        axes.select('.y-axis')
          .transition()
          .duration(duration)
          .call(axisY);
      }

      // d3-axis wants to helpfully add font-family:sans-serif, here we remove it
      axes.select('.x-axis').attr('font-family', null);
      axes.select('.y-axis').attr('font-family', null);

      // Conclude the initialization process.
      this.axisPlotInitialized = true;
    },

    setXLabel(msg) {
      const {
        margin,
        dwidth,
        dheight,
        svg,
      } = this;

      labelAxis(svg.select('.label.x'),
        msg,
        bbox => dwidth / 2 - bbox.width / 2,
        bbox => dheight + margin.bottom / 2 + bbox.height / 2,
        0);
    },

    setYLabel(msg) {
      const {
        margin,
        dheight,
        svg,
      } = this;

      labelAxis(svg.select('.label.y'),
        msg,
        bbox => -margin.left / 2 - bbox.height / 2,
        bbox => dheight / 2 + bbox.width / 2,
        -90);
    },
  },
};
