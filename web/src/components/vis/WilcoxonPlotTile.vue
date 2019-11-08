<script>
import WilcoxonPlot from '@/components/vis/WilcoxonPlot.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';
import { SET_DATASET_SELECTED_COLUMNS } from '../../store/actions.type';

export default {
  components: {
    WilcoxonPlot,
    ToolbarOption,
    VisTileLarge,
  },

  mixins: [plotData('wilcoxon')],

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

  computed: {
    selected: {
      get() {
        return (this.dataset.selectedColumns || []).slice();
      },
      set(columns) {
        this.$store.dispatch(SET_DATASET_SELECTED_COLUMNS, { dataset_id: this.id, columns });
      },
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(title="Wilcoxon Test", :loading="plot.loading", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Highlight Threshold
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minCorrelation(v-model="threshold", label="0", thumb-label="always",
              hide-details, min="0", max="0.1", step="0.001")
  wilcoxon-plot(v-if="plot.data", :data="plot.data", :threshold="threshold", v-model="selected")
</template>

<style scoped>
.minCorrelation {
  padding-top: 16px;
}

.minCorrelation >>> .v-input__slot::after {
  content: "0.1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
