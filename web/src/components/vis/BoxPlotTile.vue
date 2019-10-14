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
vis-tile(title="Metabolite Box Plot", :loading="false", svg-download)
  boxplot-plot(
      v-if="dataset.ready",
      :rows="chartData")
  template(#help)
    p.
      This chart shows the distribution of each metabolite's measurements using
      a series of box plots.

    p.
      Each metabolite appears along the y-axis, with a horizontal box plot
      showing the four quartile values, emphasizing the interquartile range
      (IQR) with solid bars. Individual outliers appear as well: normal ones,
      falling at least 1.5 IQRs away from the interquartile range, as dots;
      and "far-out" outliers, falling at least 3 IQRs away from the
      interquartile range, as larger dots.

    p.
      Hovering the mouse pointer over various parts of the plot will show
      detailed information in a tooltip. These include details of the different
      quartile ranges, and the values of outliers.

</template>
