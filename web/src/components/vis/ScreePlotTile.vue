<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ScreePlot,
    VisTile,
  },

  mixins: [plotData('pca')],

  props: {
    id: {
      required: true,
      type: String,
    },
  },

  data() {
    return {
      numComponentsText: '10',
      showCutoffs: true,
    };
  },

  computed: {
    numComponents() {
      return Number.parseInt(this.numComponentsText, 10);
    },
  },
};
</script>

<template lang="pug">
vis-tile(v-if="plot", title="PCA Scree Plot", :loading="plot.loading", svg-download)
  scree-plot(
      :eigenvalues="getPlotDataProperty('sdev')",
      :num-components="numComponents",
      :show-cutoffs="showCutoffs")
  template(v-slot:controls)
    v-menu(bottom, offset-y, left, :min-width="150", :close-on-content-click="false")
      template(v-slot:activator="{ on }")
        v-btn(v-on="on", icon)
          v-icon.mdi.mdi-dots-vertical

      v-card.pa-1(flat)
        v-layout.px-2(column)
          v-text-field.py-2(
              hide-details,
              type="number",
              label="Principal Components",
              min="1",
              outline,
              v-model="numComponentsText")
          v-switch.py-2(v-model="showCutoffs", label="Diagnostic cutoffs", hide-details)
  template(v-slot:help)
    p.
      This chart shows a Principal Component Analysis (PCA) scree plot. By
      default, it displays ten components.

    p.
      Hovering the mouse pointer over the points in the chart shows a tooltip
      displaying the eigenvalue for that component, along with the percentage of
      total variance accounted for by that component, as well as the cumulative
      percentage of total variance taken up by that component and all those
      preceding it.

    p.
      Vertical diagnostic cutoff lines are also plotted after the components
      providing a cumulative percentage of total variance of 50%, 80%, and 90%.

    p.
      The settings menu enables selection of how many principal components to
      plot, as well as whether the diagnostic cutoff lines are displayed.

</template>
