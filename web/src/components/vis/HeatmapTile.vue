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

  computed: {
    values() {
      return this.dataset.validatedMeasurements;
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Heatmap", expanded
    :loading="plot.loading || !dataset.ready || !values || values.data.length === 0")
  template(#default="wrapper")
    heatmap(
        v-if="plot && dataset.ready && values",
        :values="values",
        :column-clustering="plot.data.column",
        :row-clustering="plot.data.row")
</template>
