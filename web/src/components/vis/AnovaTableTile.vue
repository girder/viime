<script>
import AnovaTable from '@/components/vis/AnovaTable.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    AnovaTable,
    ToolbarOption,
    VisTileLarge,
  },

  mixins: [plotData('anova')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      threshold: 0.05,
    };
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Anova Table", :loading="plot.loading", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Highlight Threshold
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minCorrelation(v-model="threshold", label="0", thumb-label,
              hide-details, min="0", max="0.1", step="0.001")
  anova-table(:data="plot.data", :threshold="threshold")
</template>

<style scoped>
.minCorrelation >>> .v-input__slot::after {
  content: "0.1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
