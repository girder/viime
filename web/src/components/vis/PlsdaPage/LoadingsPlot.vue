<script>
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from '@/components/vis/mixins/plotData';

export default {
  components: {
    LoadingsPlot,
    VisTile,
  },

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

    showCrosshairs: {
      type: Boolean,
      required: true,
    },

    loadings: {
      type: Array,
      required: true,
    },
  },

};
</script>

<template lang="pug">
vis-tile(title="PLS-DA Loadings Plot", :loading="false", svg-download)
  loadings-plot(
      :points="loadings",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-crosshairs="showCrosshairs")
  //- template(v-slot:help)
  //-   include ../help/LoadingsPlotHelp.pug
</template>
