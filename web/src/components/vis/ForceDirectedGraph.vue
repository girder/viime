<script>
import resize from 'vue-resize-directive';
import {
  forceSimulation, forceManyBody, forceCollide, forceLink, forceCenter,
} from 'd3-force';
import { select } from 'd3-selection';
import { scalePow, scaleLinear } from 'd3-scale';


function extent(arr) {
  return arr.reduce((acc, d) => ({
    xMin: Math.min(acc.xMin, d.x),
    xMax: Math.max(acc.xMax, d.x),
    yMin: Math.min(acc.yMin, d.y),
    yMax: Math.max(acc.yMax, d.y),
  }), {
    xMin: Number.POSITIVE_INFINITY,
    xMax: Number.NEGATIVE_INFINITY,
    yMin: Number.POSITIVE_INFINITY,
    yMax: Number.NEGATIVE_INFINITY,
  });
}

export default {
  directives: {
    resize,
  },
  props: {
    radius: {
      type: Number,
      default: 10,
      required: false,
    },
    nodes: { // {id: string, color?: string}[]
      type: Array,
      required: true,
    },
    edges: { // {source: string, target: string, value: number}[]
      type: Array,
      required: true,
    },
    linkDistance: {
      type: Number,
      required: true,
    },
    showNodeLabels: {
      type: Boolean,
      default: false,
      required: false,
    },
    showEdgeLabels: {
      type: Boolean,
      default: false,
      required: false,
    },
    minStrokeValue: {
      type: Number,
      default: 0,
      required: false,
    },
  },
  data() {
    return {
      width: 0,
      height: 0,
      simulation: this.initSimulation(),
      refsMounted: false, // to force an rendering after mounting
    };
  },
  computed: {
    reactivePlotUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.update();
      return '';
    },
    strokeScale() {
      return scalePow().exponent(2).domain([this.minStrokeValue, 1]).range([1, 8])
        .clamp(true);
    },
  },
  mounted() {
    this.onResize();
    this.refsMounted = true;
  },
  unmounted() {
    this.simulation.stop();
  },
  methods: {
    initSimulation() {
      const f = forceSimulation();
      f.force('many', forceManyBody());
      f.force('center', forceCenter());
      f.force('collide', forceCollide());
      f.force('link', forceLink().id(d => d.id).strength(d => d.value));
      return f;
    },
    async update() {
      this.simulation.stop();
      const svg = select(this.$refs.svg);
      svg.attr('width', this.width).attr('height', this.height);

      // work on local copy since D3 manipulates the data structure
      const localNodes = this.nodes.map(d => Object.assign({}, d));
      const nodes = svg.select('g.nodes').selectAll('g').data(localNodes)
        .join(enter => enter.append('g').html('<title></title><circle></circle><text></text>'));
      nodes.select('circle')
        .attr('r', this.radius)
        .style('fill', d => d.color);
      nodes.select('title').text(d => d.id);
      nodes.select('text').text(d => d.id);

      const localEdges = this.edges.map(d => Object.assign({}, d));
      const edges = svg.select('g.edges').selectAll('g').data(localEdges)
        .join(enter => enter.append('g').html('<title></title><line></line><text></text>'));
      edges.select('line').style('stroke-width', d => this.strokeScale(d.value));
      edges.select('title').text(d => `${d.source} - ${d.target}: ${d.value.toFixed(3)}`);
      edges.select('text').text(d => d.value.toFixed(3));

      // towards center of screen
      this.simulation.nodes(localNodes);
      this.simulation.force('link').distance(this.linkDistance).links(localEdges);
      this.simulation.force('center').x(this.width / 2).y(this.height / 2);
      this.simulation.force('collide').radius(this.radius);
      this.simulation.alpha(1).restart();
      this.simulation.tick(250);
      for (let i = 0; i < 50; i += 1) {
        this.simulation.tick();
        const simNodes = this.simulation.nodes();
        const domain = extent(simNodes);
        const xScale = scaleLinear().domain([domain.xMin, domain.xMax])
          .range([this.radius, this.width - this.radius]);
        const yScale = scaleLinear().domain([domain.yMin, domain.yMax])
          .range([this.radius, this.height - this.radius]);
        nodes
          .attr('transform', d => `translate(${xScale(d.x)},${yScale(d.y)})`);
        edges.select('line')
          .attr('x1', d => xScale(d.source.x))
          .attr('y1', d => yScale(d.source.y))
          .attr('x2', d => xScale(d.target.x))
          .attr('y2', d => yScale(d.target.y));
        edges.select('text')
          .attr('transform', d => `translate(${xScale((d.source.x + d.target.x) / 2)},${yScale((d.source.y + d.target.y) / 2)})`);
        /* eslint-disable-next-line no-await-in-loop */
        await new Promise(resolve => window.setTimeout(resolve, 20));
      }
    },
    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width;
      this.height = bb.height;
    },
  },
};
</script>

<template lang="pug">
.main(v-resize:throttle="onResize")
  svg.svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactivePlotUpdate")
    g.edges(:class="{ hideLabels: !this.showEdgeLabels }")
    g.nodes(:class="{ hideLabels: !this.showNodeLabels }")
</template>

<style scoped>
.main {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  display: flex;
}

.nodes >>> g > circle,
.edges >>> g > line {
  fill-opacity: 0.6;
  stroke-opacity: 0.6;
}

.nodes >>> circle {
  fill: steelblue;
}

.nodes >>> text {
  transform: translate(12px,0);
  dominant-baseline: central;
}

.hideLabels >>> text {
  display: none;
}

.nodes >>> g:hover > circle,
.edges >>> g:hover > line {
  fill-opacity: 1;
  stroke-opacity: 1;
}

.edges >>> line {
  fill: none;
  stroke: rgb(189, 189, 189);
}

.edges >>> text {
  dominant-baseline: central;
  text-anchor: middle;
}

</style>
