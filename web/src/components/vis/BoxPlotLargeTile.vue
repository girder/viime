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
        values: df.data.map(row => row[i]),
      }));

      if (this.metaboliteFilter) {
        data = data.filter(d => this.metaboliteFilter.apply(d.name));
      }

      // if (this.sampleFilter && this.$refs.sample) {
      //   // split by groups
      //   const enabled = new Set(this.sampleFilter.filter);
      //   const bak = data;
      //   data = [];
      //   df.rowNames.map(())
      //   bak.forEach((entry) => {

      //   });
      // }

      return data;
    },

    groupSize() {
      return !this.sampleFilter ? 1 : this.sampleFilter.filter.length;
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="dataset", title="Metabolite Box Plot", :loading="false",
    download, expanded)
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter")
    sample-filter(ref='sample', :dataset="dataset", v-model="sampleFilter",
        title="Group By", empty-option="No grouping")

  boxplot-plot.main(
      v-if="dataset.ready",
      :rows="chartData", :group-size="groupSize")
</template>

<style scoped>
.main {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
