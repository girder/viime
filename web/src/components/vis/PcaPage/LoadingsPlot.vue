<script>
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from '@/components/vis/mixins/plotData';

export default {
  components: {
    LoadingsPlot,
    VisTile,
  },

  mixins: [
    plotData('loadings'),
  ],

  props: {
    id: {
      type: String,
      required: true,
    },

    pcX: {
      type: Number,
      validator: prop => Number.isInteger(prop),
      required: true,
    },

    pcY: {
      type: Number,
      validator: prop => Number.isInteger(prop),
      required: true,
    },

    showCrosshairs: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<template lang="pug">
vis-tile(title="PCA Loadings Plot", :loading="plot.loading", svg-download)
  loadings-plot(
      :points="plot.data",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-crosshairs="showCrosshairs")
</template>
