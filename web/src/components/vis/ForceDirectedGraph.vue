<script>
import resize from 'vue-resize-directive';
import {
  forceSimulation, forceManyBody, forceCollide, forceLink, forceCenter,
} from 'd3-force';
import { select } from 'd3-selection';

export default {
  directives: {
    resize,
  },
  props: {
    nodes: { // {id: string}[]
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
    minValue: {
      type: Number,
      default: Number.NaN,
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
      f.force('link', forceLink().id(d => d.id).strength(d => Math.abs(d.value)));
      return f;
    },
    update() {
      console.log('rebind');
      this.simulation.stop();
      const svg = select(this.$refs.svg);
      svg.attr('width', this.width).attr('height', this.height);

      // work on local copy since D3 manipulates the data structure
      const localNodes = this.nodes.map(d => Object.assign({}, d));
      const nodes = svg.select('g.nodes').selectAll('circle').data(localNodes)
        .join((enter) => {
          const c = enter.append('circle').attr('r', 10);
          c.append('title');
          return c;
        });
      nodes.select('title').text(d => d.id);
      this.simulation.nodes(localNodes);

      let localEdges = Number.isNaN(this.minValue) ? this.edges.slice()
        : this.edges.filter(d => d.value >= this.minValue);
      localEdges = localEdges.map(d => Object.assign({}, d));
      const edges = svg.select('g.edges').selectAll('line').data(localEdges).join('line');
      const link = this.simulation.force('link');
      link.distance(this.linkDistance).links(localEdges);

      // towards center of screen
      this.simulation.force('center').x(this.width / 2).y(this.height / 2);

      this.simulation.on('tick', () => {
        nodes
          .attr('cx', d => d.x)
          .attr('cy', d => d.y);
        edges
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);
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
div.main(v-resize:throttle="onResize")
  svg.svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg")
    g.edges
    g.nodes
  span(style="display: none") {{ reactivePlotUpdate }}
</template>

<style lang="css" scoped>
.main {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}

.nodes >>> * {
  fill: steelblue;
  opacity: 0.8;
}

.nodes >>> *:hover {
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
