<script>
import BoxplotPlot from './BoxPlot.vue';
import VisTileLarge from './VisTileLarge.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';

export default {
  components: {
    BoxplotPlot,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
  },

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },

    chartData() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return [];
      }
      return df.columnNames.map((name, i) => ({
        name,
        values: df.data.map(row => row[i]),
      }));
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="dataset", title="Metabolite Box Plot", :loading="false",
    download, expanded)
  boxplot-plot.main(
      v-if="dataset.ready",
      :rows="chartData")
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
