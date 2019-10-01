<script>
import BoxplotPlot from './BoxPlot.vue';
import VisTile from './VisTile.vue';

export default {
  components: {
    BoxplotPlot,
    VisTile,
  },

  props: {
    width: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    height: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
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
vis-tile(title="Boxplot Plot", :loading="false")
  template(#default="wrapper")
    boxplot-plot(
        v-if="dataset.ready",
        :width="width * wrapper.scale",
        :height="height * wrapper.scale",
        :rows="chartData")
</template>
