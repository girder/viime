<script>
import { csvFormat } from 'd3-dsv';
import AnovaTable from './AnovaTable.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import plotData from './mixins/plotData';
import { SET_DATASET_SELECTED_COLUMNS } from '../../store/actions.type';
import { downloadCSV } from '../../utils/exporter';

export default {
  components: {
    AnovaTable,
    ToolbarOption,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
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
      metaboliteColor: null,
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
      let data = this.plot.data && this.plot.data.data ? this.plot.data.data : [];

      if (this.metaboliteFilter) {
        const filter = this.metaboliteFilter.apply;
        data = data.filter((row) => filter(row.Metabolite));
      }
      if (this.metaboliteColor) {
        const colorer = this.metaboliteColor.apply;
        data = data.map((row) => ({ ...row, color: colorer(row.Metabolite) }));
      }

      return {
        ...base,
        data,
      };
    },
  },

  methods: {
    downloadTable() {
      downloadCSV(csvFormat(this.tableData.data, ['Metabolite', 'Group', 'Intercept', ...this.tableData.pairs]), 'ANOVA');
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Anova Table", :loading="plot.loading", expanded)
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter", hide-selection)
    metabolite-colorer(:dataset="dataset", v-model="metaboliteColor", hide-selection,
        empty-option="No Color")

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Highlight Threshold
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minCorrelation(v-model="threshold", label="0", thumb-label="always",
              hide-details, min="0", max="0.1", step="0.001")
    v-btn(flat, dark, block, @click="downloadTable")
      v-icon.mr-2 {{ $vuetify.icons.save }}
      | Download Table
  anova-table.horizontalScrollable(
      v-if="plot.data",
      :data="tableData",
      :threshold="threshold",
      :error-msg="plot.data.error || ''",
      v-model="selected")
</template>

<style scoped>
.horizontalScrollable {
  position: absolute;
}

.minCorrelation {
  padding-top: 16px;
}

.minCorrelation >>> .v-input__slot::after {
  content: "0.1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
