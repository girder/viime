<script>
import { combination } from 'js-combinatorics';
import VolcanoPlot from './VolcanoPlot.vue';
import VisTileLarge from './VisTileLarge.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import plotData from './mixins/plotData';

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

    chartData() {
      let data = this.plot.data && this.plot.data.data ? this.plot.data.data : [];

      const c = this.combination || this.defaultCombination;
      const scoreKey = c;
      const foldChangeKey = `${c} Log2FoldChange`;

      data = data.map(row => ({
        name: row.Metabolite,
        pValue: row[scoreKey],
        log2FoldChange: row[foldChangeKey],
      }));

      if (this.metaboliteFilter && this.metaboliteFilter) {
        const filter = this.metaboliteFilter.apply;
        data = data.filter(d => filter(d.name));
      }
      if (this.metaboliteColor) {
        const colorer = this.metaboliteColor.apply;
        data = data.map(row => ({ ...row, color: colorer(row.name) }));
      }

      return data;
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
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter")
    metabolite-colorer(:dataset="dataset", v-model="metaboliteColor",
        empty-option="No Color")

  volcano-plot.main(
      v-if="plot.data",
      :rows="chartData")
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
</style>
