<script>
import BoxplotPlot from './BoxPlot.vue';
import VisTileLarge from './VisTileLarge.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import SampleFilter from '../toolbar/SampleFilter.vue';

export default {
  components: {
    BoxplotPlot,
    VisTileLarge,
    MetaboliteFilter,
    SampleFilter,
  },

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      metaboliteFilter: null,
      sampleFilter: null,
    };
  },

  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },

    chartData() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return [];
      }
      let data = df.columnNames.map((name, i) => ({
        name,
        values: df.data.map((row) => row[i]),
      }));

      if (this.metaboliteFilter && this.metaboliteFilter.option) {
        data = data.filter((d) => this.metaboliteFilter.apply(d.name));
      }

      if (this.sampleFilter && this.sampleFilter.option) {
        // split by groups
        const groups = this.sampleFilter.groupBy(df.rowNames);
        data.forEach((row) => {
          const vs = row.values;
          delete row.values;
          row.groups = groups.map((group) => ({
            name: group.name,
            color: group.color,
            values: group.indices.map((i) => vs[i]),
          }));
        });
      }

      return data;
    },

    groups() {
      return this.sampleFilter && this.sampleFilter.option ? this.sampleFilter.filter : [];
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="dataset", title="Metabolite Box Plot", :loading="false",
    download, expanded)
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter")
    sample-filter(:dataset="dataset", v-model="sampleFilter",
        title="Group By", empty-option="No grouping")

  boxplot-plot.main(
      v-if="dataset.ready",
      :rows="chartData",
      :groups="groups")
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
