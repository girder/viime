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
  template(#default="wrapper")
    loadings-plot(
        :width="width * wrapper.scale",
        :height="height * wrapper.scale",
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
</template>
