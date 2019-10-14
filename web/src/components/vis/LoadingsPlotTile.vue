<script>
import LoadingsPlot from './LoadingsPlot.vue';
import VisTile from './VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    LoadingsPlot,
    VisTile,
  },

  mixins: [plotData('loadings')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      pcXval: '1',
      pcYval: '2',
      showCrosshairs: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval, 10);
    },

    pcY() {
      return Number.parseInt(this.pcYval, 10);
    },
  },
};

</script>

<template lang="pug">
vis-tile(v-if="plot", title="PCA Loadings Plot", :loading="plot.loading", svg-download)
  loadings-plot(
      :points="plot.data",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-crosshairs="showCrosshairs")
  template(v-slot:controls)
    v-menu(bottom, offset-y, left, :min-width="150", :close-on-content-click="false")
      template(v-slot:activator="{ on }")
        v-btn(v-on="on", icon)
          v-icon.mdi.mdi-dots-vertical

      v-card.pa-1(flat)
        v-layout(column)
          v-text-field.pa-2(
              hide-details,
              type="number",
              label="PC (X Axis)",
              min="1",
              outline,
              v-model="pcXval")
          v-text-field.pa-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              outline,
              v-model="pcYval")
          v-switch.ma-2(hide-details, v-model="showCrosshairs", label="Show crosshairs")
  template(v-slot:help)
    p.
      This chart shows a Principal Component Analysis (PCA) loadings plot. The
      Pearson correlation of each metabolite with the displayed principal
      components is plotted in a scatter plot. A reticle appears at the origin
      for help in interpreting the plotted points as vectors.

    p.
      Hovering the mouse pointer over a point shows the name of the metabolite,
      as well as exact values for correlation with the two principal components.

    p.
      The menu contains options for selecting which components to show in the
      plot, as well as a toggle for turning the reticle display on and off.

</template>
