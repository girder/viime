<script>
import Heatmap from './Heatmap.vue';
import VisTileLarge from './VisTileLarge.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    Heatmap,
    VisTileLarge,
  },

  mixins: [plotData('heatmap')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Heatmap", :loading="plot.loading", expanded)
  template(#default="wrapper")
    heatmap(
        v-if="plot && dataset.ready",
        :values="dataset.validatedMeasurements",
        :column-clustering="plot.data.column",
        :row-clustering="plot.data.row")
</template>
