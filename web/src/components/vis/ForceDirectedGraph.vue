<script>
import resize from 'vue-resize-directive';
import {
  forceSimulation, forceManyBody, forceCollide, forceLink, forceX, forceY, forceCenter,
} from 'd3-force';
import { select, event as d3Event } from 'd3-selection';
import { scalePow } from 'd3-scale';
import { zoom, zoomTransform } from 'd3-zoom';
import { drag } from 'd3-drag';


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
    showLabels: {
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
      zoom: zoom(),
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
      f.force('x', forceX().strength(0.01));
      f.force('y', forceY().strength(0.01));
      f.force('center', forceCenter());
      f.force('collide', forceCollide());
      f.force('link', forceLink().id(d => d.id).strength(d => d.value));
      f.on('tick', () => this.tick());
      return f;
    },
    stopTicker() {
      // not a observed data element
      if (this.simulationTicker != null && this.simulationTicker >= 0) {
        this.simulationTicker = window.clearTimeout(this.simulationTicker);
        this.simulationTicker = -1;
      }
    },
    startTicker() {
      const ticker = (remaining) => {
        this.simulation.tick();
        this.tick();
        if (remaining > 0) {
          this.simulationTicker = window.setTimeout(ticker, 20, remaining - 1);
        }
      };
      ticker(50);
    },
    tick() {
      const svg = select(this.$refs.svg);
      const nodes = svg.select('g.nodes').selectAll('g');
      const edges = svg.select('g.edges').selectAll('g');

      const t = zoomTransform(svg.node());

      nodes.select('circle')
        .attr('transform', d => `translate(${t.applyX(d.x)},${t.applyY(d.y)})`);
      nodes.select('text')
        .attr('transform', d => `translate(${t.applyX(d.x)},${t.applyY(d.y)})`);

      edges.select('line')
        .attr('x1', d => t.applyX(d.source.x))
        .attr('y1', d => t.applyY(d.source.y))
        .attr('x2', d => t.applyX(d.target.x))
        .attr('y2', d => t.applyY(d.target.y));
      edges.select('text')
        .attr('transform', d => `translate(${t.applyX((d.source.x + d.target.x) / 2)},${t.applyY((d.source.y + d.target.y) / 2)})`);
    },
    update() {
      const { simulation, stopTicker } = this;

      simulation.stop();
      this.stopTicker();

      const svg = select(this.$refs.svg);
      svg.attr('width', this.width).attr('height', this.height);

      svg.call(this.zoom
        .extent([[0, 0], [this.width, this.height]])
        .on('zoom', () => this.tick()));

      // work on local copy since D3 manipulates the data structure
      const localNodes = this.nodes.map(d => Object.assign({}, d));
      const nodes = svg.select('g.nodes').selectAll('g').data(localNodes)
        .join(enter => enter.append('g').html('<title></title><circle></circle><text dx="12"></text>'));


      function dragged() {
        const node = d3Event.subject;
        node.fx = d3Event.x;
        node.fy = d3Event.y;
      }

      function dragstarted() {
        select(this).raise();
        stopTicker();
        simulation.alphaTarget(0.3).restart();
        dragged();
      }

      function resetPinned(d) {
        delete d.fx;
        delete d.fy;
        stopTicker();
        simulation.restart();
      }

      function dragended() {
        simulation.alphaTarget(0);
      }

      nodes.select('circle')
        .attr('r', this.radius)
        .style('fill', d => d.color)
        .on('click', resetPinned)
        .call(drag()
          .container(function container() {
            return this.parentNode.parentNode;
          })
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended));
      nodes.select('title').text(d => d.id);
      nodes.select('text').text(d => d.id);

      const localEdges = this.edges.map(d => Object.assign({}, d));
      const edges = svg.select('g.edges').selectAll('g').data(localEdges)
        .join(enter => enter.append('g').html('<title></title><line></line><text></text>'));
      edges.select('line').style('stroke-width', d => this.strokeScale(d.value));
      edges.select('title').text(d => `${d.source} - ${d.target}: ${d.value.toFixed(3)}`);
      edges.select('text').text(d => d.value.toFixed(3));

      // towards center of screen
      simulation.nodes(localNodes);
      simulation.force('link').distance(this.linkDistance).links(localEdges);
      simulation.force('x').x(this.width / 2);
      simulation.force('y').y(this.height / 2);
      simulation.force('center').x(this.width / 2).y(this.height / 2);
      simulation.force('collide').radius(this.radius);

      simulation.alpha(1).restart().stop().tick(250); // forward 250 ticks
      this.tick();
      this.startTicker();
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
    g.zoom
      g.edges(:class="{ hideLabels: !this.showLabels }")
      g.nodes(:class="{ hideLabels: !this.showLabels }")
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
  cursor: grab;
}

.nodes >>> text {
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
