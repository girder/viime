<script>

export default {
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
  },
  mounted() {
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
      if (!this.$refs.column) {
        return;
      }
      // TODO
    },
    updateMatrix() {
      if (!this.$refs.column) {
        return;
      }
      // TODO
    },
  },
};
</script>

<template lang="pug">
.grid
  svg.column(ref="column", :width="width * 0.7", :height="height * 0.3", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
  svg.row(ref="row", :width="width * 0.3", :height="height * 0.7", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
  canvas.matrix(ref="matrix", :width="width * 0.7", :height="height * 0.7",
      :data-update="reactiveMatrixUpdate")
</template>

<style scoped>
.grid {
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
