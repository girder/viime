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

    columnHierarchy() {
      return this.computeHierarchy(this.columnClustering, this.column,
        this.width, this.height);
    },

    rowHierarchy() {
      const root = this.computeHierarchy(this.rowClustering, this.row,
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
    computeHierarchy(node, { collapsed, focus }, layoutWidth, layoutHeight) {
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

      const l = cluster()
        .size([layoutWidth * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH,
          layoutHeight * DENDOGRAM_RATIO - this.padding2])
        .separation(() => 1);

      return l(root);
    },
    updateTree(ref, root, wrapper, horizontalLayout) {
      if (!ref) {
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
      inner.classed('focussed', d => wrapper.focus === d.data);

      inner.attr('transform', d => `translate(${d.x},${d.y})`);
    },
    updateColumn() {
      this.updateTree(this.$refs.column, this.columnHierarchy, this.column, true);
    },
    updateRow() {
      this.updateTree(this.$refs.row, this.rowHierarchy, this.row, false);
    },
    updateLabel(ref, wrapper, labels, horizontalLayout) {
      if (!ref) {
        return;
      }
      const svg = select(ref);
      const text = svg.selectAll('text').data(labels, d => d.data.name).join((enter) => {
        const r = enter.append('text')
          .attr('transform', d => (horizontalLayout ? `translate(${d.x},0)rotate(-90)` : `translate(0,${d.y})`));
        return r;
      });
      const { hovered } = wrapper;

      let bandwidth = 10;
      if (labels.length >= 2) {
        bandwidth = (horizontalLayout ? (labels[1].x - labels[0].x) : (labels[1].y - labels[0].y));
      }
      svg.style('font-size', `${bandwidth < 5 ? bandwidth : Math.min(bandwidth - 2, 12)}px`);

      text.classed('selected', d => d.data.indices.some(l => hovered.has(l)));
      text.text(d => d.data.name);
      text.attr('transform', d => (horizontalLayout ? `translate(${d.x},0)rotate(-90)` : `translate(0,${d.y})`));
    },
    updateColumnLabel() {
      this.updateLabel(this.$refs.collabel, this.column, this.columnLeaves, true);
    },
    updateRowLabel() {
      this.updateLabel(this.$refs.rowlabel, this.row, this.rowLeaves, false);
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const width = this.width * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH;
      const height = this.height * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH;
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.canvas.width = width;
      ctx.canvas.height = height;
      ctx.clearRect(0, 0, width, height);
      const rows = this.rowLeaves;
      const columns = this.columnLeaves;
      const {
        valueScale,
        values,
      } = this;
      const hoveredRow = this.row.hovered;
      const hoveredColumn = this.column.hovered;

      const w = width / columns.length;
      const h = height / rows.length;

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
  svg.column(ref="column", :width="width * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH",
      :height="height * DENDOGRAM_RATIO", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.edges(:transform="`translate(0,${padding})`")
    g.nodes(:transform="`translate(0,${padding})`")
  svg.row(ref="row", :width="width * DENDOGRAM_RATIO",
      :height="height * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.edges(:transform="`translate(${padding},0)`")
    g.nodes(:transform="`translate(${padding},0)`")
  canvas.matrix(ref="matrix", :data-update="reactiveMatrixUpdate",
      @mousemove="canvasMouseMove($event)", @mouseleave="canvasMouseLeave()")
  svg.collabel(ref="collabel", :width="width * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH",
      :height="LABEL_WIDTH", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnLabelUpdate")
  svg.rowlabel(ref="rowlabel", :width="LABEL_WIDTH",
      :height="height * (1 - DENDOGRAM_RATIO) - LABEL_WIDTH",
      :data-update="reactiveRowLabelUpdate")
</template>

<style scoped>
.grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 8px;
  bottom: 8px;
  display: grid;
  grid-template-areas: "d column dl"
    "row matrix rlabel"
    "rc clabel ll";
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
.collabel {
  grid-area: clabel;
}

.collabel >>> text {
  dominant-baseline: central;
  text-anchor: end;
}

.rowlabel {
  grid-area: rlabel;
}

.rowlabel >>> text {
  dominant-baseline: central;
}

.rowlabel >>> text.selected,
.collabel >>> text.selected {
  font-size: 150%;
  fill: orange;
}

.edges >>> path {
  fill: none;
  stroke-width: 2;
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
.nodes >>> .focussed {
  opacity: 1;
}


</style>
