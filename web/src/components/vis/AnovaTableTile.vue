<script>
import AnovaTable from './AnovaTable.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import plotData from './mixins/plotData';
import { SET_DATASET_SELECTED_COLUMNS } from '../../store/actions.type';

export default {
  components: {
    AnovaTable,
    ToolbarOption,
    VisTileLarge,
    MetaboliteFilter,
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
      metaboliteFilter: null,
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
    tableData() {
      const base = this.plot.data || { data: [] };
      if (!this.metaboliteFilter) {
        return base;
      }

      const filter = this.metaboliteFilter.apply;
      return {
        ...base,
        data: base.data.filter(row => filter(row.Metabolite)),
      };
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Anova Table", :loading="plot.loading", expanded)
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter", hide-selection)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Highlight Threshold
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minCorrelation(v-model="threshold", label="0", thumb-label="always",
              hide-details, min="0", max="0.1", step="0.001")
  anova-table(:data="tableData", :threshold="threshold", v-model="selected")
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
