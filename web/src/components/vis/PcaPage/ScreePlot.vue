<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from '@/components/vis/mixins/plotData';

export default {
  components: {
    ScreePlot,
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

    numComponents: {
      type: Number,
      validator: (prop) => Number.isInteger(prop) && prop > 0,
      required: true,
    },

    showCutoffs: {
      type: Boolean,
      required: true,
    },
  },

  computed: {
    ready() {
      return this.$store.getters.ready(this.id);
    },

    eigenvalues() {
      return this.maybeData('sdev', []);
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
vis-tile(title="PCA Scree Plot", :loading="plot.loading", svg-download)
  scree-plot(
      :eigenvalues="eigenvalues",
      :pc-x="pcX",
      :pc-y="pcY",
      :num-components="numComponents",
      :show-cutoffs="showCutoffs")
  template(v-slot:help)
    include ../help/ScreePlotHelp.pug
</template>
