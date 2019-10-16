<script>
import resize from 'vue-resize-directive';
import { hierarchy, cluster } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateBlues } from 'd3-scale-chromatic';
import { select, event } from 'd3-selection';

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
const LABEL_WIDTH = 150;

const MDI_PLUS_CIRCLE = '&#xF417;';
const MDI_MINUS_CIRCLE = '&#xF376;';
const MDI_STAR_CIRCLE = '&#xF4CF;';

export const heatmapLayouts = [
  { label: 'Auto', value: 'auto' },
  { label: 'Square Cells', value: 'squareCells' },
  { label: 'Square Matrix', value: 'squareMatrix' },
];


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
    rowConfig: { // { dendogram: boolean, colorer?: (name) => string }
      type: Object,
      default: () => ({ dendogram: true, colorer: null }),
    },
    columnConfig: { // { dendogram: boolean, colorer?: (name) => string }
      type: Object,
      default: () => ({ dendogram: true, colorer: null }),
    },
    layout: { // { dendogram: boolean }
      type: String,
      validate: v => heatmapLayouts.find(d => d.value === v),
      default: heatmapLayouts[0].value,
    },
  },
  data() {
    return {
      padding: 8,
      width: 0,
      height: 0,
      refsMounted: false,
      column: {
        hovered: new Set(),
        collapsed: new Set(),
        focus: null,
      },
      row: {
        hovered: new Set(),
        collapsed: new Set(),
        focus: null,
      },
      rnode: null,
      cnode: null,
      DENDOGRAM_RATIO,
      LABEL_WIDTH,
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
    reactiveRowLabelUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateRowLabel();
      return '';
    },
    reactiveColumnLabelUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateColumnLabel();
      return '';
    },

    columnTree() {
      return this.computeTree(this.columnClustering, this.column);
    },

    columnHierarchy() {
      return this.computeHierarchy(this.columnTree, this.matrixWidth, this.height);
    },

    rowTree() {
      return this.computeTree(this.rowClustering, this.row);
    },

    rowHierarchy() {
      const root = this.computeHierarchy(this.rowTree, this.matrixHeight, this.width);
      if (!root) {
        return root;
      }
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
      return this.columnTree ? this.columnTree.leaves() : [];
    },
    rowLeaves() {
      return this.rowTree ? this.rowTree.leaves() : [];
    },
    columnDendogramHeight() {
      return this.columnConfig.dendogram ? this.height * DENDOGRAM_RATIO : 0;
    },
    rowDendogramWidth() {
      return this.rowConfig.dendogram ? this.width * DENDOGRAM_RATIO : 0;
    },
    matrixDimensions() {
      let width = this.width - this.rowDendogramWidth - LABEL_WIDTH;
      let height = this.height - this.columnDendogramHeight - LABEL_WIDTH;
      if (this.layout === 'squareCells') {
        const wx = width / this.columnLeaves.length;
        const hy = height / this.rowLeaves.length;
        const ci = Math.min(wx, hy);
        width = ci * this.columnLeaves.length;
        height = ci * this.rowLeaves.length;
      } else if (this.layout === 'squareMatrix') {
        width = Math.min(width, height);
        height = width;
      }
      return { width, height };
    },
    matrixWidth() {
      return this.matrixDimensions.width;
    },
    matrixHeight() {
      return this.matrixDimensions.height;
    },
    fontSize() {
      const wx = this.matrixWidth / this.columnLeaves.length - 2;
      const hy = this.matrixHeight / this.rowLeaves.length - 2;

      return Math.min(wx, hy, 12);
    },
  },
  mounted() {
    this.onResize();
    this.refsMounted = true;
  },

  methods: {
    computeTree(node, { collapsed, focus }) {
      if (!node) {
        return null;
      }
      const injectIndices = (s) => {
        if (typeof s.index === 'number') {
          s.indices = [s.index];
          s.names = [s.name];
        } else {
          s.indices = [].concat(...s.children.map(injectIndices));
          s.names = [].concat(...s.children.map(c => c.names));
          s.name = s.names.join(', ');
        }
        return s.indices;
      };

      injectIndices(node);

      let root = hierarchy(node,
        d => (collapsed.has(d) ? [] : (d.children || [])))
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      if (focus) {
        // find the focus node and it is the new root
        root.each((n) => {
          if (n.data === focus) {
            root = n;
          }
        });
      }
      return root;
    },
    computeHierarchy(root, layoutWidth, layoutHeight) {
      if (!root) {
        return null;
      }
      const l = cluster()
        .size([layoutWidth, layoutHeight * DENDOGRAM_RATIO - this.padding2])
        .separation(() => 1);
      return l(root);
    },
    updateTree(ref, root, wrapper, config, horizontalLayout) {
      if (!ref || !config.dendogram || !root) {
        return;
      }
      const svg = select(ref);
      const edges = svg.select('g.edges').selectAll('path').data(root.links()).join((enter) => {
        const r = enter.append('path');
        r.on('mouseenter', (d) => {
          wrapper.hovered = new Set(d.target.data.indices);
        }).on('mouseleave', () => {
          wrapper.hovered = new Set();
        });
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

      edges.attr('d', horizontalLayout ? renderVerticalLinks : renderHorizontalLinks);

      const innerNodes = root.descendants().filter(d => d.data.indices.length > 1);
      const inner = svg.select('g.nodes').selectAll('g').data(innerNodes).join((enter) => {
        const r = enter.append('g')
          .html(`<circle r="${padding}"></circle><text><text><title></title>`)
          .attr('transform', d => `translate(${d.x},${d.y})`);
        r.on('click', (d) => {
          if (wrapper.focus === d.data) {
            wrapper.focus = null;
          } else if (event.ctrlKey || event.shiftKey) {
            wrapper.focus = d.data;
          } else if (wrapper.collapsed.has(d.data)) {
            wrapper.collapsed.delete(d.data);
            wrapper.collapsed = new Set(wrapper.collapsed);
          } else {
            wrapper.collapsed.add(d.data);
            wrapper.collapsed = new Set(wrapper.collapsed);
          }
        }).on('mouseenter', (d) => {
          wrapper.hovered = new Set(d.data.indices);
        }).on('mouseleave', () => {
          wrapper.hovered = new Set();
        });
        return r;
      });

      inner.select('text').html((d) => {
        if (wrapper.focus === d.data) {
          return MDI_STAR_CIRCLE;
        }
        return collapsed.has(d.data) ? MDI_PLUS_CIRCLE : MDI_MINUS_CIRCLE;
      });
      inner.select('title').text(d => d.data.name);
      inner.classed('collapsed', d => collapsed.has(d.data));
      inner.classed('focused', d => wrapper.focus === d.data);

      inner.attr('transform', d => `translate(${d.x},${d.y})`);
    },
    updateColumn() {
      if (this.columnDendogramHeight === 0) {
        return;
      }
      this.updateTree(this.$refs.column, this.columnHierarchy, this.column,
        this.columnConfig, true);
    },
    updateRow() {
      if (this.rowDendogramWidth === 0) {
        return;
      }
      this.updateTree(this.$refs.row, this.rowHierarchy, this.row, this.rowConfig, false);
    },
    updateLabel(ref, wrapper, labels, colorer, isColumn) {
      if (!ref) {
        return;
      }
      const div = select(ref);
      const text = div.selectAll('div').data(labels).join('div');
      const { hovered } = wrapper;

      text.classed('selected', d => d.data.indices.some(l => hovered.has(l)));
      text.text(d => d.data.name);

      const combineColor = (names) => {
        if (names.length === 1) {
          return colorer(names[0]);
        }
        const frequencies = new Map();
        names.forEach((name) => {
          const color = colorer(name);
          frequencies.set(color, (frequencies.get(color) || 0) + 1);
        });
        // most frequent color
        return Array.from(frequencies.entries()).sort((a, b) => b[1] - a[1])[0][0];
      };

      const toColor = (names) => {
        const color = combineColor(names);
        return `linear-gradient(${isColumn ? 'to top' : 'to right'}, ${color} 0, ${color} 5px, transparent 5px)`;
      };

      text.classed('color', colorer != null);
      text.style('background', !colorer ? null : (d => toColor(d.data.names)));
    },
    updateColumnLabel() {
      this.updateLabel(this.$refs.collabel, this.column, this.columnLeaves,
        this.columnConfig.colorer, true);
    },
    updateRowLabel() {
      this.updateLabel(this.$refs.rowlabel, this.row, this.rowLeaves,
        this.rowConfig.colorer, false);
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.canvas.width = this.matrixWidth;
      ctx.canvas.height = this.matrixHeight;
      ctx.clearRect(0, 0, this.matrixWidth, this.matrixHeight);
      const rows = this.rowLeaves;
      const columns = this.columnLeaves;
      const {
        valueScale,
        values,
      } = this;
      const hoveredRow = this.row.hovered;
      const hoveredColumn = this.column.hovered;

      const w = this.matrixWidth / columns.length;
      const h = this.matrixHeight / rows.length;

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
          ctx.lineTo(j * w, ctx.canvas.height);
          ctx.moveTo(j * w + w, 0);
          ctx.lineTo(j * w + w, ctx.canvas.height);
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
      if (rnode !== this.rnode || cnode !== this.cnode) {
        this.rnode = rnode;
        this.cnode = cnode;
        this.row.hovered = new Set(rnode.indices);
        this.column.hovered = new Set(cnode.indices);
        canvas.title = `${rnode.name} x ${cnode.name} = ${aggregate(this.values.data, rnode.indices, cnode.indices)}`;
      }
    },
    canvasMouseLeave() {
      this.row.hovered = new Set();
      this.column.hovered = new Set();
      this.rnode = null;
      this.cnode = null;
    },
  },
};
</script>

<template lang="pug">
.grid(v-resize:throttle="onResize")
  svg.column(ref="column", v-show="columnConfig.dendogram",
      :width="matrixWidth",
      :height="height * DENDOGRAM_RATIO", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.edges(:transform="`translate(0,${padding})`")
    g.nodes(:transform="`translate(0,${padding})`")
  svg.row(ref="row", v-show="rowConfig.dendogram",
      :width="width * DENDOGRAM_RATIO",
      :height="matrixHeight", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.edges(:transform="`translate(${padding},0)`")
    g.nodes(:transform="`translate(${padding},0)`")
  canvas.matrix(ref="matrix", :data-update="reactiveMatrixUpdate",
      @mousemove="canvasMouseMove($event)", @mouseleave="canvasMouseLeave()")
  .collabel(ref="collabel",
      :style="{fontSize: fontSize+'px', width: this.matrixWidth+'px', height: LABEL_WIDTH+'px'}",
      :data-update="reactiveColumnLabelUpdate")
  .rowlabel(ref="rowlabel",
      :style="{fontSize: fontSize+'px', width: LABEL_WIDTH+'px', height: this.matrixHeight+'px'}",
      :data-update="reactiveRowLabelUpdate")
</template>

<style scoped>
.grid {
  position: absolute;
  top: 4px;
  left: 4px;
  right: 8px;
  bottom: 8px;
  display: grid;
  grid-template-areas: "d column dl"
    "row matrix rlabel"
    "rc clabel ll";
  justify-content: center;
  align-content: center;
}

.column {
  grid-area: column;
}
.row {
  grid-area: row;
}
.matrix {
  grid-area: matrix;
}
.collabel {
  grid-area: clabel;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow: hidden;
}

.collabel >>> div {
  writing-mode: tb;
  transform: rotate(-180deg);
  justify-content: center;
}

.collabel >>> div.color {
  padding-bottom: 7px;
}

.rowlabel {
  grid-area: rlabel;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.rowlabel >>> div.color {
  padding-left: 7px;
}

.collabel >>> div,
.rowlabel >>> div {
  flex: 1 1 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
}

.rowlabel >>> .selected,
.collabel >>> .selected {
  color: orange;
}

.edges >>> path {
  fill: none;
  stroke-width: 1;
  stroke: black;
}

.edges >>> path.selected {
  stroke: orange;
}

.nodes >>> g {
  opacity: 0;
  font: normal normal normal 24px/1 "Material Design Icons";
  fill: black;
  cursor: pointer;
  font-size: 150%;
  user-select: none;
  text-anchor: middle;
  dominant-baseline: central;
}

.nodes >>> g > circle {
  fill: white;
}

.nodes >>> g:hover {
  opacity: 1;
  fill: orange;
}

.nodes >>> g:hover > text {
  fill: orange;
}

.nodes >>> .collapsed,
.nodes >>> .focused {
  opacity: 1;
}


</style>
