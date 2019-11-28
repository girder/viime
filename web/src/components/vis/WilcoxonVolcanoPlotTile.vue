<script>
import VolcanoPlot from './VolcanoPlot.vue';
import VisTileLarge from './VisTileLarge.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import plotData from './mixins/plotData';
import {combination} from 'js-combinatorics';

export default {
  components: {
    VolcanoPlot,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
    ToolbarOption,
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
      score: 'Wilcoxon',
      scores: [
        {value: 'Wilcoxon', label: 'Wilcoxon'},
        {value: 'Bonferroni', label: 'Bonferroni'},
        {value: 'Hochberg', label: 'Hochberg'},
      ],
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
      const levels = this.dataset.groupLevels.slice().sort((a,b) => a.name.localeCompare(b.name));

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

      const combination = this.combination || this.defaultCombination;
      const scoreKey = this.hasMoreThanTwoGroups ? `${combination} ${this.score}` : this.score;
      const foldChangeKey = this.hasMoreThanTwoGroups ? `${combination} Log2FoldChange` : 'Log2FoldChange';

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
vis-tile-large(v-if="dataset", title="Metabolite Wilcoxon Volanco Plot", :loading="false",
    download, expanded)
  template(#controls)
    toolbar-option(:value="score", @change="score = $event", title="p-Value", :options="scores")
    toolbar-option(v-if="hasMoreThanTwoGroups",
        :value="combination || defaultCombination", @change="combination = $event", title="Group Combiation",
        :options="combinations")
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
