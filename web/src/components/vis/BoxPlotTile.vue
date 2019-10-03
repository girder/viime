<script>
import BoxplotPlot from './BoxPlot.vue';
import VisTile from './VisTile.vue';

export default {
  components: {
    BoxplotPlot,
    VisTile,
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
vis-tile(title="Boxplot Plot", :loading="false", svg-download)
  boxplot-plot(
      v-if="dataset.ready",
      :rows="chartData")
</template>
