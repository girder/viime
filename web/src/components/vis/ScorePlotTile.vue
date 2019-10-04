<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  mixins: [plotData('pca')],

  props: {
    id: {
      type: String,
      required: true,
    },
    columns: {
      required: true,
      type: Array,
    },
  },

  data() {
    return {
      pcXval: '1',
      pcYval: '2',
      showEllipses: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval, 10);
    },

    pcY() {
      return Number.parseInt(this.pcYval, 10);
    },

    pcCoords() {
      return this.getPlotDataProperty('x', []);
    },

    rowLabels() {
      return this.getPlotDataProperty('rows', []);
    },

    groupLabels() {
      return this.getPlotDataProperty('labels', {});
    },

    eigenvalues() {
      return this.getPlotDataProperty('sdev', []);
    },
  },
};

</script>

<template lang="pug">
vis-tile(v-if="plot", title="PCA Score Plot", :loading="plot.loading", svg-download)
  score-plot(
      v-if="plot && dataset.ready",
      :pc-coords="pcCoords",
      :row-labels="rowLabels",
      :group-labels="groupLabels",
      :eigenvalues="eigenvalues",
      :columns="columns",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-ellipses="showEllipses")
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
              label="PC (X Axis)",
              min="1",
              outline,
              v-model="pcXval")
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              outline,
              v-model="pcYval")
          v-switch.py-2(v-model="showEllipses", label="Data ellipses", hide-details)
</template>
