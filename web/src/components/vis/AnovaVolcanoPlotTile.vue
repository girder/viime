<script>
import { combination } from 'js-combinatorics';
import VolcanoPlot from './VolcanoPlot.vue';
import VisTileLarge from './VisTileLarge.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import plotData from './mixins/plotData';
import { SET_DATASET_SELECTED_COLUMNS } from '../../store/actions.type';

export default {
  components: {
    VolcanoPlot,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
    ToolbarOption,
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
      combination: null,
      metaboliteFilter: null,
      metaboliteColor: null,
      minFoldChange: 1,
      minLogP: 1,
    };
  },

  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },

    hasMoreThanTwoGroups() {
      return this.dataset && this.dataset.groupLevels.length > 2;
    },

    combinations() {
      if (!this.dataset) {
        return [];
      }
      const levels = this.dataset.groupLevels.slice().sort((a, b) => a.name.localeCompare(b.name));

      return combination(levels, 2).map(([a, b]) => ({
        value: `${a.name} - ${b.name}`,
        label: `${a.label} - ${b.label}`,
      }));
    },

    defaultCombination() {
      const c = this.combinations;
      return c.length > 0 ? c[0].value : '';
    },

    selected: {
      get() {
        return (this.dataset.selectedColumns || []).slice();
      },
      set(columns) {
        this.$store.dispatch(SET_DATASET_SELECTED_COLUMNS, { dataset_id: this.id, columns });
      },
    },

    chartData() {
      let data = this.plot.data && this.plot.data.data ? this.plot.data.data : [];

      const c = this.combination || this.defaultCombination;
      const scoreKey = c;
      const foldChangeKey = `${c} Log2FoldChange`;

      data = data.map((row) => ({
        name: row.Metabolite,
        pValue: row[scoreKey],
        log2FoldChange: row[foldChangeKey],
      }));

      if (this.metaboliteFilter && this.metaboliteFilter) {
        const filter = this.metaboliteFilter.apply;
        data = data.filter((d) => filter(d.name));
      }
      if (this.metaboliteColor) {
        const colorer = this.metaboliteColor.apply;
        data = data.map((row) => ({ ...row, color: colorer(row.name) }));
      }

      return data;
    },
  },
  methods: {
    setSelection() {
      this.selected = this.chartData.map((d) => ({
        name: d.name,
        x: d.log2FoldChange,
        y: -Math.log10(d.pValue),
      }))
        .filter((d) => Math.abs(d.x) >= this.minFoldChange && d.y >= this.minLogP)
        .map((d) => d.name);
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="dataset", title="Metabolite Anova Volanco Plot", :loading="false",
    download, expanded)
  template(#controls)
    toolbar-option(v-if="hasMoreThanTwoGroups",
        :value="combination || defaultCombination", @change="combination = $event",
        title="Group Combination", :options="combinations")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Min Fold Change
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minFoldChange(v-model="minFoldChange", label="0", thumb-label="always",
              hide-details, min="0", max="3", step="0.05")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Min Log P-value
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minLogP(v-model="minLogP", label="0", thumb-label="always",
              hide-details, min="0", max="5", step="0.05")
    v-btn(flat, dark, block, @click="setSelection")
      v-icon.mr-2 {{ $vuetify.icons.plusMultiple }}
      | Select Metabolites
    metabolite-colorer(:dataset="dataset", v-model="metaboliteColor",
        empty-option="No Color")

  // can refactor v-if to use optional chaining when viime is updated to Vue 3
  volcano-plot.main(
      v-if="plot.data && !plot.data.error",
      :rows="chartData",
      :min-fold-change="minFoldChange",
      :min-log-p="minLogP")
  // same for value prop here
  v-alert(
      type="error",
      v-text="`ANOVA failed. ${plot.data && plot.data.error ? plot.data.error : ''}`",
      :value="plot.data && plot.data.error")
</template>

<style scoped>
.main {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}

.minFoldChange {
  padding-top: 16px;
}

.minFoldChange >>> .v-input__slot::after {
  content: "3";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}

.minLogP {
  padding-top: 16px;
}

.minLogP >>> .v-input__slot::after {
  content: "5";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
