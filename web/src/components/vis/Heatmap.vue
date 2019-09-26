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

      return cluster().size([this.width * 0.8, this.height * 0.2])(root);
    },

    rowHierarchy() {
      const root = hierarchy(this.rowClustering)
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      return cluster().size([this.height * 0.8, this.width * 0.2])(root);
    },
    valueScale() {
      return scaleSequential(interpolateBlues).domain(extent(this.values.data));
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
      edges.attr('d', d => `
        M${d.target.x},${d.target.y}
        C${d.target.x},${d.target.y - 10}
         ${d.source.x},${d.source.y + 10}
         ${d.source.x},${d.source.y}
      `);
    },
    updateRow() {
      if (!this.$refs.row) {
        return;
      }
      const svg = select(this.$refs.row);
      const root = this.rowHierarchy;
      const edges = svg.select('g.edges').selectAll('path').data(root.links()).join('path');
      edges.attr('d', d => `
        M${d.target.y},${d.target.x}
        C${d.target.y - 10},${d.target.x}
         ${d.source.y + 10},${d.source.x}
         ${d.source.y},${d.source.x}
      `);
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

      const w = ctx.canvas.width / this.values.columnNames.length;
      const h = ctx.canvas.height / this.values.rowNames.length;

      const rows = this.rowHierarchy.leaves();
      const columns = this.columnHierarchy.leaves();

      rows.forEach((rnode) => {
        const i = rnode.data.index;
        columns.forEach((cnode) => {
          const j = cnode.data.index;
          const v = this.values.data[i][j];
          ctx.fillStyle = this.valueScale(v);
          ctx.fillRect(j * w, i * h, w, h);
        });
      });
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
.grid(v-resize:throttle="onResize")
  svg.column(ref="column", :width="width * 0.8", :height="height * 0.2", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.nodes
    g.edges
  svg.row(ref="row", :width="width * 0.2", :height="height * 0.8", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.nodes
    g.edges
  canvas.matrix(ref="matrix", :width="width * 0.8", :height="height * 0.8",
      :data-update="reactiveMatrixUpdate")
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

.nodes >>> circle {
  fill: steelblue;
}

.edges >>> path {
  fill: none;
  stroke: black;
}
</style>
