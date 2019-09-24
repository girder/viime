<script>
import BoxplotPlot from './BoxplotPlot.vue';
import VisTile from './VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    BoxplotPlot,
    VisTile,
  },

  mixins: [plotData('boxplot')],

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

  data() {
    return {
    };
  },

  computed: {
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
vis-tile(v-if="plot", title="Boxplot Plot", :loading="plot.loading")
  template(#default="wrapper")
    boxplot-plot(
        v-if="plot && dataset.ready",
        :width="width * wrapper.scale",
        :height="height * wrapper.scale",
        :rows="chartData")
</template>
