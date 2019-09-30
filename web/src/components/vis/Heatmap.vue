<script>
import resize from 'vue-resize-directive';
import { hierarchy, cluster } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateBlues } from 'd3-scale-chromatic';
import { select } from 'd3-selection';
import 'd3-transition';

function extent(arr) {
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  arr.forEach(row => row.forEach((v) => {
    if (v < min) {
      min = v;
    }
    if (v > max) {
      max = v;
    }
  }));
  return [min, max];
}

function aggregate(arr, is, js) {
  if (is.length === 1 && js.length === 1) {
    return arr[is[0]][js[0]];
  }
  // average
  const l = is.length * js.length;
  const sum = is.reduce((acc, i) => acc + js.reduce((acc2, j) => acc2 + arr[i][j], 0), 0);
  return sum / l;
}

const DENDOGRAM_RATIO = 0.2;

const MDI_PLUS_CIRCLE = '&#xF417;';
const MDI_MINUS_CIRCLE = '&#xF376;';


export default {
  directives: {
    resize,
  },
  props: {
    values: { // {columnNames: string[], rowNames: string[], data: number[][]}
      type: Object,
      default: () => ({ columnNames: [], rowNames: [], data: [] }),
    },
    columnClustering: { // ITreeNode
      type: Object,
      default: null,
    },
    rowClustering: { // ITreeNode
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      padding: 8,
      width: 100,
      height: 100,
      refsMounted: false,
      duration: 500,
      column: {
        hovered: new Set(),
        collapsed: new Set(),
      },
      row: {
        hovered: new Set(),
        collapsed: new Set(),
      },
      DENDOGRAM_RATIO,
    };
  },
  computed: {
    padding2() {
      return this.padding * 2;
    },
    reactiveColumnUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateColumn();
      return '';
    },
    reactiveRowUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateRow();
      return '';
    },
    reactiveMatrixUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateMatrix();
      return '';
    },

    columnHierarchy() {
      return this.computeHierarchy(this.columnClustering, this.column.collapsed,
        this.width, this.height);
    },

    rowHierarchy() {
      const root = this.computeHierarchy(this.rowClustering, this.row.collapsed,
        this.height, this.width);
      root.each((node) => {
        const t = node.x;
        node.x = node.y;
        node.y = t;
      });
      return root;
    },
    valueScale() {
      return scaleSequential(interpolateBlues).domain(extent(this.values.data));
    },
    columnLeaves() {
      return this.columnHierarchy.leaves();
    },
    rowLeaves() {
      return this.rowHierarchy.leaves();
    },
  },
  mounted() {
    this.onResize();
    this.refsMounted = true;
  },

  methods: {
    computeHierarchy(node, collapsed, layoutWidth, layoutHeight) {
      const injectIndices = (s) => {
        if (typeof s.index === 'number') {
          s.indices = [s.index];
        } else {
          s.indices = [].concat(...s.children.map(injectIndices));
          s.name = s.children.map(d => d.name).join(',');
        }
        return s.indices;
      };

      injectIndices(node);

      const root = hierarchy(node,
        d => (collapsed.has(d) ? [] : (d.children || [])))
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      const l = cluster().size([layoutWidth * (1 - DENDOGRAM_RATIO) - this.padding2,
        layoutHeight * DENDOGRAM_RATIO - this.padding2])
        .separation(() => 1);

      return l(root);
    },
    updateTree(ref, root, wrapper, horizontalLayout) {
      if (!ref) {
        return;
      }
      const svg = select(ref);
      const edges = svg.select('g.edges').selectAll('path').data(root.links(), d => `${d.source.data.name}-${d.target.data.name}`).join((enter) => {
        const r = enter.append('path');
        r.on('mouseenter', (d) => {
          wrapper.hovered = new Set(d.target.data.indices);
        }).on('mouseleave', () => {
          wrapper.hovered = new Set();
        }).style('opacity', 0);
        return r;
      });
      const { hovered, collapsed } = wrapper;
      const { padding } = this;

      edges.classed('selected', d => d.target.data.indices.some(l => hovered.has(l)));

      const renderVerticalLinks = d => `
        M${d.target.x},${d.target.y + (d.target.children ? 0 : padding)}
        L${d.target.x},${d.source.y}
        L${d.source.x},${d.source.y}
      `;
      const renderHorizontalLinks = d => `
        M${d.target.x + (d.target.children ? 0 : padding)},${d.target.y}
        L${d.source.x},${d.target.y}
        L${d.source.x},${d.source.y}
      `;

      edges.transition('move').duration(this.duration).attr('d', horizontalLayout ? renderVerticalLinks : renderHorizontalLinks).transition('fadeIn')
        .style('opacity', 1);

      const innerNodes = root.descendants().filter(d => d.data.indices.length > 1);
      const inner = svg.select('g.nodes').selectAll('text').data(innerNodes, d => d.data.name).join((enter) => {
        const r = enter.append('text')
          .attr('transform', d => `translate(${d.x},${d.y})`);
        r.on('click', (d) => {
          if (wrapper.collapsed.has(d.data)) {
            wrapper.collapsed.delete(d.data);
          } else {
            wrapper.collapsed.add(d.data);
          }
          wrapper.collapsed = new Set(wrapper.collapsed);
        }).on('mouseenter', (d) => {
          wrapper.hovered = new Set(d.data.indices);
        }).on('mouseleave', () => {
          wrapper.hovered = new Set();
        });
        return r;
      });

      inner.html(d => (collapsed.has(d.data) ? MDI_MINUS_CIRCLE : MDI_PLUS_CIRCLE));
      inner.classed('collapsed', d => collapsed.has(d.data));

      inner.transition('move').duration(this.duration)
        .attr('transform', d => `translate(${d.x},${d.y})`);
    },
    updateColumn() {
      this.updateTree(this.$refs.column, this.columnHierarchy, this.column, true);
    },
    updateRow() {
      this.updateTree(this.$refs.row, this.rowHierarchy, this.row, false);
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      const rows = this.rowLeaves;
      const columns = this.columnLeaves;
      const {
        valueScale,
        values,
      } = this;
      const hoveredRow = this.row.hovered;
      const hoveredColumn = this.column.hovered;

      const w = ctx.canvas.width / columns.length;
      const h = ctx.canvas.height / rows.length;

      ctx.strokeStyle = 'orange';


      // work on copy for speed
      const data = values.data.map(r => r.slice());

      rows.forEach((rnode, i) => {
        const rowSelected = rnode.data.indices.some(s => hoveredRow.has(s));
        columns.forEach((cnode, j) => {
          const v = aggregate(data, rnode.data.indices, cnode.data.indices);
          ctx.fillStyle = valueScale(v);
          ctx.fillRect(j * w, i * h, w, h);
        });

        if (rowSelected) {
          ctx.beginPath();
          ctx.moveTo(0, i * h);
          ctx.lineTo(ctx.canvas.width, i * h);
          ctx.moveTo(0, i * h + h);
          ctx.lineTo(ctx.canvas.width, i * h + h);
          ctx.stroke();
        }
      });

      columns.forEach((cnode, j) => {
        const columnSelected = cnode.data.indices.some(s => hoveredColumn.has(s));
        if (columnSelected) {
          ctx.beginPath();
          ctx.moveTo(j * w, 0);
          ctx.lineTo(j * w, ctx.canvas.width);
          ctx.moveTo(j * w + w, 0);
          ctx.lineTo(j * w + w, ctx.canvas.width);
          ctx.stroke();
        }
      });
    },
    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width;
      this.height = bb.height;
    },
    canvasMouseMove(evt) {
      const canvas = evt.currentTarget;
      const w = canvas.width / this.columnLeaves.length;
      const h = canvas.height / this.rowLeaves.length;

      const j = Math.floor(evt.offsetX / w);
      const i = Math.floor(evt.offsetY / h);
      const rnode = this.rowLeaves[i].data;
      const cnode = this.columnLeaves[j].data;
      this.row.hovered = new Set(rnode.indices);
      this.column.hovered = new Set(cnode.indices);
      canvas.title = `${rnode.name} x ${cnode.name} = ${aggregate(this.values.data, rnode.indices, cnode.indices)}`;
    },
    canvasMouseLeave() {
      this.row.hovered = new Set();
      this.column.hovered = new Set();
    },
  },
};
</script>

<template lang="pug">
.grid(v-resize:throttle="onResize")
  svg.column(ref="column", :width="width * (1 - DENDOGRAM_RATIO)",
      :height="height * DENDOGRAM_RATIO", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.edges(:transform="`translate(${padding},${padding})`")
    g.nodes(:transform="`translate(${padding},${padding})`")
  svg.row(ref="row", :width="width * DENDOGRAM_RATIO",
      :height="height * (1 - DENDOGRAM_RATIO)", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.edges(:transform="`translate(${padding},${padding})`")
    g.nodes(:transform="`translate(${padding},${padding})`")
  canvas.matrix(ref="matrix", :width="width * (1 - DENDOGRAM_RATIO)",
      :height="height * (1 - DENDOGRAM_RATIO)",
      :data-update="reactiveMatrixUpdate",
      @mousemove="canvasMouseMove($event)", @mouseleave="canvasMouseLeave()")
</template>

<style scoped>
.grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 8px;
  bottom: 8px;
  display: grid;
  grid-template-areas: "d column"
    "row matrix";
}

.column {
  grid-area: column;
}
.row {
  grid-area: row
}
.matrix {
  grid-area: matrix;
}

.edges >>> path {
  fill: none;
  stroke-width: 2;
  stroke: black;
}

.edges >>> path.selected {
  stroke: orange;
}

.nodes >>> text {
  opacity: 0;
  font: normal normal normal 24px/1 "Material Design Icons";
  fill: black;
  cursor: pointer;
  font-size: 150%;
  user-select: none;
  text-anchor: middle;
  dominant-baseline: central;
}

.nodes >>> text:hover {
  opacity: 1;
  fill: orange;
}

.nodes >>> .collapsed {
  opacity: 1;
}


</style>
