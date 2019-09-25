<script>
import resize from 'vue-resize-directive';
import { hierarchy, cluster } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateBlues } from 'd3-scale-chromatic';

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
      const root = hierarchy(this.columnClustering);

      return root;
    },

    rowHierarchy() {
      const root = hierarchy(this.rowClustering);

      return root;
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
      // TODO
    },
    updateRow() {
      if (!this.$refs.row) {
        return;
      }
      // TODO
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

      const w = ctx.canvas.width / this.values.columnNames.length;
      const h = ctx.canvas.height / this.values.rowNames.length;

      this.values.data.forEach((row, i) => {
        row.forEach((v, j) => {
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
  svg.row(ref="row", :width="width * 0.2", :height="height * 0.8", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
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
</style>
