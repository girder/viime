import { scaleLinear } from 'd3-scale';
import { axisBottom, axisLeft } from 'd3-axis';
import resize from 'vue-resize-directive';

function labelAxis(label, msg, xFunc, yFunc, rot) {
  const text = label.select('text')
    .html(`${msg}`);
  const bbox = text.node().getBBox();
  label.attr('transform', `translate(${xFunc(bbox)},${yFunc(bbox)}) rotate(${rot})`)
    .style('opacity', 1.0);
}

export const axisPlot = {
  directives: {
    resize,
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
      duration: 500,
      svg: null,
      width: 100,
      height: 100,
      refsMounted: false, // to force an rendering after mounting
    };
  },
  computed: {
    reactiveUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      if (this.$refs.svg) {
        this.update();
      }
      return '';
    },
    dwidth() {
      const { width, margin } = this;
      return width - margin.left - margin.right;
    },
    dheight() {
      const { height, margin } = this;
      return height - margin.top - margin.bottom;
    },
    xrange() {
      // This value (and `yrange` below) are defined as computed properties with
      // a constant function to provide flexibility for clients of this mixin,
      // which may want these properties to be reactive based on other, private
      // properties.
      return [-1, 1];
    },
    yrange() {
      // (See note above for `xrange`.)
      return [-1, 1];
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
  mounted() {
    this.onResize();
    this.refsMounted = true;
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
          .attr('transform', `translate(0,${dheight})`)
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

      if (!svg.node()) {
        return;
      }

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

      if (!svg.node()) {
        return;
      }

      labelAxis(svg.select('.label.y'),
        msg,
        bbox => -margin.left / 2 - bbox.height / 2,
        bbox => dheight / 2 + bbox.width / 2,
        -90);
    },
    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width;
      this.height = bb.height;
    },
  },
};
