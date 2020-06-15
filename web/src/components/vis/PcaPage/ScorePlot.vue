<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from '@/components/vis/mixins/plotData';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  mixins: [
    plotData('pca'),
  ],

  props: {
    id: {
      type: String,
      required: true,
    },

    pcX: {
      type: Number,
      validator: (prop) => Number.isInteger(prop),
      required: true,
    },

    pcY: {
      type: Number,
      validator: (prop) => Number.isInteger(prop),
      required: true,
    },

    showEllipses: {
      type: Boolean,
      required: true,
    },
  },

  computed: {
    ready() {
      return this.$store.getters.ready(this.id);
    },

    pcCoords() {
      return this.maybeData('x', []);
    },

    rowLabels() {
      return this.maybeData('rows', []);
    },

    groupLabels() {
      return this.maybeData('labels', {});
    },

    eigenvalues() {
      return this.maybeData('sdev', []);
    },

    columns() {
      return this.dataset.column.data;
    },
  },

  methods: {
    maybeData(key, dflt) {
      const {
        plot,
      } = this;

      return plot.data ? plot.data[key] : dflt;
    },
  },
};
</script>

<template lang="pug">
vis-tile(title="PCA Score Plot", :loading="plot.loading", svg-download)
  score-plot(
      :pc-coords="pcCoords",
      :row-labels="rowLabels",
      :colors="dataset.groupLevels",
      :group-labels="groupLabels",
      :eigenvalues="eigenvalues",
      :columns="columns",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-ellipses="showEllipses")
  template(v-slot:help)
    include ../help/ScorePlotHelp.pug
</template>
