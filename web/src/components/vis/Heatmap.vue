<script>
import resize from 'vue-resize-directive';
import { hierarchy, cluster } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateBlues } from 'd3-scale-chromatic';
import { select } from 'd3-selection';

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

const DENDOGRAM_RATIO = 0.2;

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
      width: 100,
      height: 100,
      refsMounted: false,
      hoveredRow: new Set(),
      hoveredColumn: new Set(),
      DENDOGRAM_RATIO,
    };
  },
  computed: {
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
      const root = hierarchy(this.columnClustering)
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      return cluster().size([this.width * (1 - DENDOGRAM_RATIO), this.height * DENDOGRAM_RATIO])
        .separation(() => 1)(root);
    },

    rowHierarchy() {
      const root = hierarchy(this.rowClustering)
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      return cluster().size([this.height * (1 - DENDOGRAM_RATIO), this.width * DENDOGRAM_RATIO])
        .separation(() => 1)(root);
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
    updateColumn() {
      if (!this.$refs.column) {
        return;
      }
      const svg = select(this.$refs.column);
      const root = this.columnHierarchy;
      const edges = svg.select('g.edges').selectAll('path').data(root.links()).join('path');
      const hovered = this.hoveredColumn;

      edges.attr('d', d => `
        M${d.target.x},${d.target.y}
        C${d.target.x},${(d.target.y + d.source.y) * 0.5}
         ${d.source.x},${(d.target.y + d.source.y) * 0.5}
         ${d.source.x},${d.source.y}
      `).on('mouseenter', (d) => {
        this.hoveredColumn = new Set(d.target.leaves().map(l => l.data.index));
      }).on('mouseleave', () => {
        this.hoveredColumn = new Set();
      }).classed('selected', d => d.target.leaves().some(l => hovered.has(l.data.index)));
    },
    updateRow() {
      if (!this.$refs.row) {
        return;
      }
      const svg = select(this.$refs.row);
      const root = this.rowHierarchy;
      const edges = svg.select('g.edges').selectAll('path').data(root.links()).join('path');
      const hovered = this.hoveredRow;
      edges.attr('d', d => `
        M${d.target.y},${d.target.x}
        C${(d.target.y + d.source.y) * 0.5},${d.target.x}
         ${(d.target.y + d.source.y) * 0.5},${d.source.x}
         ${d.source.y},${d.source.x}
      `).on('mouseenter', (d) => {
        this.hoveredRow = new Set(d.target.leaves().map(l => l.data.index));
      }).on('mouseleave', () => {
        this.hoveredRow = new Set();
      }).classed('selected', d => d.target.leaves().some(l => hovered.has(l.data.index)));
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

      const w = ctx.canvas.width / this.values.columnNames.length;
      const h = ctx.canvas.height / this.values.rowNames.length;

      const rows = this.rowLeaves;
      const columns = this.columnLeaves;

      ctx.strokeStyle = 'orange';

      const {
        valueScale,
        hoveredRow,
        hoveredColumn,
        values,
      } = this;

      // work on copy for speed
      const data = values.data.map(r => r.slice());

      rows.forEach((rnode, i) => {
        const rowSelected = hoveredRow.has(rnode.data.index);
        columns.forEach((cnode, j) => {
          const v = data[rnode.data.index][cnode.data.index];
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
        const columnSelected = hoveredColumn.has(cnode.data.index);
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
      const w = canvas.width / this.values.columnNames.length;
      const h = canvas.height / this.values.rowNames.length;

      const j = Math.floor(evt.offsetX / w);
      const i = Math.floor(evt.offsetY / h);
      const rnode = this.rowLeaves[i].data;
      const cnode = this.columnLeaves[j].data;
      this.hoveredRow = new Set([rnode.index]);
      this.hoveredColumn = new Set([cnode.index]);
      canvas.title = `${rnode.name} x ${cnode.name} = ${this.values.data[rnode.index][cnode.index]}`;
    },
    canvasMouseLeave() {
      this.hoveredRow = new Set();
      this.hoveredColumn = new Set();
    },
  },
};
</script>

<template lang="pug">
.grid(v-resize:throttle="onResize")
  svg.column(ref="column", :width="width * (1 - DENDOGRAM_RATIO)",
      :height="height * DENDOGRAM_RATIO", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.edges
  svg.row(ref="row", :width="width * DENDOGRAM_RATIO",
      :height="height * (1 - DENDOGRAM_RATIO)", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.edges
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
  right: 0;
  bottom: 0;
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

</style>
