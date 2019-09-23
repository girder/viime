<script>
import resize from 'vue-resize-directive';
import {
  forceSimulation, forceManyBody, forceCollide, forceLink, forceCenter,
} from 'd3-force';
import { select } from 'd3-selection';
import { scaleLinear } from 'd3-scale';


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
    nodeFilter: {
      type: Function,
      default: null,
      required: false,
    },
    edges: { // {source: string, target: string, value: number}[]
      type: Array,
      required: true,
    },
    edgesFilter: {
      type: Function,
      default: null,
      required: false,
    },
    linkDistance: {
      type: Number,
      required: true,
    },
    showLabels: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      width: 0,
      height: 0,
      simulation: this.initSimulation(),
      initialRun: false,
    };
  },
  computed: {
    reactivePlotUpdate() {
      if (!this.initialRun) {
        return '';
      }
      this.update();
      // to indicate that it has changed
      return Math.random().toString();
    },
  },
  mounted() {
    this.onResize();
    this.initialRun = true;
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
    update() {
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
      const edges = svg.select('g.edges').selectAll('line').data(localEdges).join('line');

      // towards center of screen
      this.simulation.nodes(localNodes);
      this.simulation.force('link').distance(this.linkDistance).links(localEdges);
      this.simulation.force('center').x(this.width / 2).y(this.height / 2);
      this.simulation.force('collide').radius(this.radius);


      this.simulation.on('tick', () => {
        const simNodes = this.simulation.nodes();
        const domain = extent(simNodes);
        const xScale = scaleLinear().domain([domain.xMin, domain.xMax])
          .range([this.radius, this.width - this.radius]);
        const yScale = scaleLinear().domain([domain.yMin, domain.yMax])
          .range([this.radius, this.height - this.radius]);
        nodes
          .attr('transform', d => `translate(${xScale(d.x)},${yScale(d.y)})`);
        edges
          .attr('x1', d => xScale(d.source.x))
          .attr('y1', d => yScale(d.source.y))
          .attr('x2', d => xScale(d.target.x))
          .attr('y2', d => yScale(d.target.y));
      });


      this.simulation.alpha(1).restart();
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
  svg.svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.edges
    g.nodes(:class="{ hideLabels: !this.showLabels }")
  span(style="display: none") {{ reactivePlotUpdate }}
</template>

<style scoped>
.main {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}

.nodes >>> g {
  opacity: 0.8;
}

.nodes >>> circle {
  fill: steelblue;
}

.nodes >>> text {
  transform: translate(12px,0);
  dominant-baseline: central;
}

.nodes.hideLabels >>> text {
  display: none;
}

.nodes >>> g:hover {
  opacity: 1;
}

.edges >>> * {
  fill: none;
  opacity: 0.2;
  stroke: black;
}

.edges >>> *:hover {
  opacity: 1;
}

</style>
