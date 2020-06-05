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
    search: {
      type: Array,
      required: true,
    },
    filteredItems: {
      type: Array,
      required: true,
    },
    visibleNodes: {
      type: Number,
      default: 0,
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
    reactivePlotBoundsUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateBounds();
      return '';
    },
    strokeScale() {
      return scalePow().exponent(2).domain([this.minStrokeValue, 1]).range([1, 8])
        .clamp(true);
    },
  },
  watch: {
    search(searchedNodes) {
      // highlights nodes being searched for
      const nodes = select(this.$refs.svg).select('g.nodes').selectAll('g');
      nodes.select('circle').style('fill', d => (searchedNodes.includes(d.id) ? 'red' : d.color));
    },
    filteredItems(filteredItems) {
      // circles nodes in search results
      const nodes = select(this.$refs.svg).select('g.nodes').selectAll('g');
      nodes.select('circle').style('stroke', d => (filteredItems.includes(d.id) ? 'red' : d.color));
      nodes.select('circle').style('stroke-width', d => (filteredItems.includes(d.id) ? '2' : '1'));
    },
    visibleNodes(visibleNodes) {
      if (visibleNodes === 0) {
        this.showAllNodes();
      } else if (visibleNodes === 1) {
        this.showOnlyWithinOneStep(this.search);
      } else if (visibleNodes === 2) {
        this.showOnlyWithinTwoSteps(this.search);
      }
    },
  },
  mounted() {
    this.onResize();
    this.refsMounted = true;
    this.update();
  },
  beforeDestroy() {
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
        if (!this.$refs.svg) {
          return;
        }
        this.simulation.tick();
        this.tick();
        if (remaining > 0) {
          this.simulationTicker = window.setTimeout(ticker, 20, remaining - 1);
        }
      };
      ticker(50);
    },
    tick() {
      if (!this.$refs.svg) {
        return;
      }
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
    tick250() {
      const sim = this.simulation.alpha(1).restart().stop();

      if (!window.requestIdleCallback) {
        sim.tick(250); // forward 250 ticks
        this.tick();
        this.startTicker();
        return;
      }

      let initialTicks = 250;

      const finishStatic = () => {
        window.requestAnimationFrame(() => {
          this.tick();
          this.startTicker();
        });
      };
      const tickStatic = (deadline) => {
        let oneTickDone = false;
        while ((!oneTickDone || deadline.timeRemaining() > 0) && initialTicks > 0) {
          initialTicks -= 1;
          sim.tick(1);
          oneTickDone = true;
        }

        if (initialTicks > 0) {
          window.requestIdleCallback(tickStatic, {
            timeout: 250, // ms
          });
        } else {
          finishStatic();
        }
      };

      window.requestIdleCallback(tickStatic, {
        timeout: 250, // ms
      });
    },

    updateBounds() {
      const { simulation } = this;

      if (!this.$refs.svg) {
        return;
      }

      const svg = select(this.$refs.svg);
      svg.attr('width', this.width).attr('height', this.height);

      svg.call(this.zoom
        .extent([[0, 0], [this.width, this.height]])
        .on('zoom', () => this.tick()));

      simulation.force('x').x(this.width / 2);
      simulation.force('y').y(this.height / 2);
      simulation.force('center').x(this.width / 2).y(this.height / 2);
      simulation.force('collide').radius(this.radius);
    },

    update() {
      const { simulation, stopTicker } = this;

      simulation.stop();
      this.stopTicker();

      if (!this.$refs.svg) {
        return;
      }

      const svg = select(this.$refs.svg);

      // work on local copy since D3 manipulates the data structure
      const localNodes = this.nodes.map(d => Object.assign({}, d));
      const nodes = svg.select('g.nodes').selectAll('g').data(localNodes)
        .join(enter => enter.append('g').html('<title></title><circle></circle><text dx="12"></text>'));


      function dragged() {
        const node = d3Event.subject.data;
        const t = zoomTransform(svg.node());
        node.fx = t.invertX(d3Event.x);
        node.fy = t.invertY(d3Event.y);
      }

      function dragstarted(d) {
        select(this)
          .raise()
          .classed('pinned', true);
        this.parentElement.querySelector('title').textContent = `${d.id} (pinned, click to unpin)`;
        stopTicker();
        simulation.alphaTarget(0.3).restart();
        dragged();
      }

      function resetPinned(d) {
        delete d.fx;
        delete d.fy;
        select(this)
          .classed('pinned', false);
        this.parentElement.querySelector('title').textContent = d.id;
        stopTicker();
        simulation.restart();
      }

      function dragended() {
        simulation.alphaTarget(0);
      }

      nodes.select('circle')
        .attr('r', this.radius)
        .style('fill', d => (this.search && this.search.includes(d.id) ? 'red' : d.color))
        .on('click', resetPinned)
        .call(drag()
          .container(function container() {
            return this.parentNode.parentNode;
          })
          .subject(data => ({ x: d3Event.x, y: d3Event.y, data }))
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended));
      nodes.select('title').text(d => d.id);
      nodes.select('text').text(d => d.id);

      const localEdges = this.edges.map(d => Object.assign({}, d));
      const edges = svg.select('g.edges').selectAll('g').data(localEdges)
        .join(enter => enter.append('g').html('<title></title><line></line><text></text>'));
      edges.select('line')
        .style('stroke-width', d => this.strokeScale(d.value))
        .style('stroke', d => d.color);
      edges.select('title').text(d => `${d.source} - ${d.target}: ${d.ori.toFixed(3)}`);
      edges.select('text').text(d => d.ori.toFixed(3));

      // towards center of screen
      simulation.nodes(localNodes);
      simulation.force('link').distance(this.linkDistance);
      simulation.force('link').links(localEdges);

      this.tick250();
    },
    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width;
      this.height = bb.height;
    },
    showAllNodes() {
      const nodes = select(this.$refs.svg).select('g.nodes').selectAll('g').select('circle');
      const edges = select(this.$refs.svg).select('g.edges').selectAll('g').select('line');
      nodes.style('visibility', '');
      edges.style('visibility', '');
    },
    showOnlyWithinOneStep(nodesConnectedTo) {
      const nodes = select(this.$refs.svg).select('g.nodes').selectAll('g').select('circle');
      const edges = select(this.$refs.svg).select('g.edges').selectAll('g').select('line');
      const visibleNodesSet = new Set(nodesConnectedTo);
      const visibleEdgesSet = new Set();
      edges.each((d) => {
        if (nodesConnectedTo.includes(d.source.id)) {
          visibleNodesSet.add(d.target.id);
          visibleEdgesSet.add(d.index);
        } else if (nodesConnectedTo.includes(d.target.id)) {
          visibleNodesSet.add(d.source.id);
          visibleEdgesSet.add(d.index);
        }
      });
      nodes.style('visibility', node => (visibleNodesSet.has(node.id) ? '' : 'hidden'));
      edges.style('visibility', edge => (visibleEdgesSet.has(edge.index) ? '' : 'hidden'));
    },
    showOnlyWithinTwoSteps(nodesConnectedTo) {
      const edges = select(this.$refs.svg).select('g.edges').selectAll('g').select('line');
      const additional = [];
      edges.each((edge) => {
        if (nodesConnectedTo.includes(edge.source.id)) {
          additional.push(edge.target.id);
        } else if (nodesConnectedTo.includes(edge.target.id)) {
          additional.push(edge.source.id);
        }
      });
      this.showOnlyWithinOneStep([...nodesConnectedTo, ...additional]);
    },
  },
};
</script>

<template lang="pug">
.main(v-resize:throttle="onResize")
  svg.svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg",
      :data-update-bounds="reactivePlotBoundsUpdate")
    g.zoom
      g.edges(:class="{ hideLabels: !this.showEdgeLabels }")
      g.nodes(:class="{ hideLabels: !this.showNodeLabels }")
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

.nodes >>> g > circle,
.edges >>> g > line {
  fill-opacity: 0.6;
  stroke-opacity: 0.6;
}

.nodes >>> circle {
  cursor: grab;
  fill: steelblue;
}

.nodes >>> circle.pinned {
  stroke-width: 2;
  stroke: black;
}

.nodes >>> circle.searched {
  stroke-width: 2;
  stroke: red;
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
