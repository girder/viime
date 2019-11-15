<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import resize from 'vue-resize-directive';
import {
  forceSimulation, forceManyBody, forceCollide, forceLink, forceX, forceY, forceCenter,
  SimulationNodeDatum, SimulationLinkDatum, ForceX, ForceCollide, ForceCenter, ForceY, ForceLink,
} from 'd3-force';
import { select, event as d3Event } from 'd3-selection';
import { scalePow } from 'd3-scale';
import { zoom, zoomTransform } from 'd3-zoom';
import { drag } from 'd3-drag';

interface IFDGNode {
  id: string;
  color?: string;
}

declare type ISimNode = IFDGNode & SimulationNodeDatum;

interface IFDGEdge {
  source: string;
  target: string;
  value: number;
  ori: number;
  color?: string;
}

interface ISimLink extends SimulationLinkDatum<ISimNode> {
  source: ISimNode;
  target: ISimNode;
  value: number;
  ori: number;
  color?: string;
}

@Component({
  directives: {
    resize,
  },
})
export default class ForceDirectedGraph extends Vue {
  @Prop({
    default: 10,
  })
  readonly radius!: number;

  @Prop({
    required: true,
  })
  readonly nodes!: IFDGNode[];

  @Prop({
    required: true,
  })
  readonly edges!: IFDGEdge[];

  @Prop({
    required: true,
  })
  readonly linkDistance!: number;

  @Prop({
    default: false,
  })
  readonly showNodeLabels!: boolean;

  @Prop({
    default: false,
  })
  readonly showEdgeLabels!: boolean;

  @Prop({
    default: 0,
  })
  readonly minStrokeValue!: number;

  width = 0;

  height= 0;

  readonly simulation = this.initSimulation();

  readonly zoom = zoom<SVGSVGElement, unknown>();

  refsMounted = false; // to force an rendering after mounting

  // not obserable
  simulationTicker: number|undefined = undefined;

  $refs!: {
    svg: SVGSVGElement
  };

  get reactivePlotUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.update();
    return '';
  }

  get reactivePlotBoundsUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateBounds();
    return '';
  }

  get strokeScale() {
    return scalePow().exponent(2).domain([this.minStrokeValue, 1]).range([1, 8])
      .clamp(true);
  }

  mounted() {
    this.onResize();
    this.refsMounted = true;
  }

  beforeDestroy() {
    this.simulation.stop();
  }

  initSimulation() {
    const f = forceSimulation<ISimNode>();
    f.force('many', forceManyBody());
    f.force('x', forceX().strength(0.01));
    f.force('y', forceY().strength(0.01));
    f.force('center', forceCenter());
    f.force('collide', forceCollide());
    f.force('link', forceLink<ISimNode, ISimLink>().id(d => d.id).strength(d => d.value));
    f.on('tick', () => this.tick());
    return f;
  }

  stopTicker() {
    // not a observed data element
    if (this.simulationTicker != null && this.simulationTicker >= 0) {
      window.clearTimeout(this.simulationTicker);
      this.simulationTicker = -1;
    }
  }

  startTicker() {
    const ticker = (remaining: number) => {
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
  }

  tick() {
    if (!this.$refs.svg) {
      return;
    }
    const svg = select(this.$refs.svg);
    const nodes = svg.select('g.nodes').selectAll<SVGGElement, ISimNode>('g');
    const edges = svg.select('g.edges').selectAll<SVGGElement, ISimLink>('g');

    const t = zoomTransform(svg.node()!);

    nodes.select('circle')
      .attr('transform', d => `translate(${t.applyX(d.x!)},${t.applyY(d.y!)})`);
    nodes.select('text')
      .attr('transform', d => `translate(${t.applyX(d.x!)},${t.applyY(d.y!)})`);

    edges.select('line')
      .attr('x1', d => t.applyX(d.source.x!))
      .attr('y1', d => t.applyY(d.source.y!))
      .attr('x2', d => t.applyX(d.target.x!))
      .attr('y2', d => t.applyY(d.target.y!));
    edges.select('text')
      .attr('transform', d => `translate(${t.applyX((d.source.x! + d.target.x!) / 2)},${t.applyY((d.source.y! + d.target.y!) / 2)})`);
  }

  tick250() {
    const sim = this.simulation.alpha(1).restart().stop();

    const idleCallback = (window as any).requestIdleCallback;

    if (!idleCallback) {
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
    const tickStatic = (deadline: { timeRemaining(): number }) => {
      let oneTickDone = false;
      while ((!oneTickDone || deadline.timeRemaining() > 0) && initialTicks > 0) {
        initialTicks -= 1;
        sim.tick(1);
        oneTickDone = true;
      }

      if (initialTicks > 0) {
        idleCallback(tickStatic, {
          timeout: 250, // ms
        });
      } else {
        finishStatic();
      }
    };

    idleCallback(tickStatic, {
      timeout: 250, // ms
    });
  }

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

    simulation.force<ForceX<ISimNode>>('x')!.x(this.width / 2);
    simulation.force<ForceY<ISimNode>>('y')!.y(this.height / 2);
    simulation.force<ForceCenter<ISimNode>>('center')!.x(this.width / 2).y(this.height / 2);
    simulation.force<ForceCollide<ISimNode>>('collide')!.radius(this.radius);
  }

  update() {
    const { simulation, stopTicker } = this;

    simulation.stop();
    this.stopTicker();

    if (!this.$refs.svg) {
      return;
    }

    const svg = select(this.$refs.svg);

    // work on local copy since D3 manipulates the data structure
    const localNodes = this.nodes.map(d => Object.assign({}, d) as ISimNode);
    const nodes = svg.select('g.nodes').selectAll('g').data(localNodes)
      .join(enter => enter.append('g').html('<title></title><circle></circle><text dx="12"></text>'));


    function dragged() {
      const node = d3Event.subject.data;
      const t = zoomTransform(svg.node()!);
      node.fx = t.invertX(d3Event.x);
      node.fy = t.invertY(d3Event.y);
    }

    function dragstarted(this: SVGCircleElement, d: ISimNode) {
      select(this)
        .raise()
        .classed('pinned', true);
      this.parentElement!.querySelector('title')!.textContent = `${d.id} (pinned, click to unpin)`;
      stopTicker();
      simulation.alphaTarget(0.3).restart();
      dragged();
    }

    function resetPinned(this: SVGCircleElement, d: ISimNode) {
      delete d.fx;
      delete d.fy;
      select(this)
        .classed('pinned', false);
      this.parentElement!.querySelector('title')!.textContent = d.id;
      stopTicker();
      simulation.restart();
    }

    function dragended() {
      simulation.alphaTarget(0);
    }

    nodes.select<SVGCircleElement>('circle')
      .attr('r', this.radius)
      .style('fill', d => d.color || null)
      .on('click', resetPinned)
      .call(drag<SVGCircleElement, ISimNode>()
        .container(function container(this: SVGCircleElement) {
          return this.parentNode!.parentNode as SVGGElement;
        })
        .subject(data => ({ x: d3Event.x, y: d3Event.y, data }))
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));
    nodes.select('title').text(d => d.id);
    nodes.select('text').text(d => d.id);

    const localEdges = this.edges.map(d => Object.assign({}, d) as unknown as ISimLink);
    const edges = svg.select('g.edges').selectAll('g').data(localEdges)
      .join(enter => enter.append('g').html('<title></title><line></line><text></text>'));
    edges.select('line')
      .style('stroke-width', d => this.strokeScale(d.value))
      .style('stroke', d => d.color || null);
    edges.select('title').text(d => `${d.source} - ${d.target}: ${d.ori.toFixed(3)}`);
    edges.select('text').text(d => d.ori.toFixed(3));

    // towards center of screen
    simulation.nodes(localNodes);
    simulation.force<ForceLink<ISimNode, ISimLink>>('link')!.distance(this.linkDistance);
    simulation.force<ForceLink<ISimNode, ISimLink>>('link')!.links(localEdges);

    this.tick250();
  }

  onResize() {
    const bb = this.$el.getBoundingClientRect();
    this.width = bb.width;
    this.height = bb.height;
  }
}
</script>

<template lang="pug">
.main(v-resize:throttle="onResize")
  svg.svg(ref="svg", :width="width", :height="height", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactivePlotUpdate", :data-update-bounds="reactivePlotBoundsUpdate")
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
