<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ScorePlot,
    VisTileLarge,
  },

  mixins: [
    plotData('pca'),
  ],

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
      showEllipses: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval);
    },

    pcY() {
      return Number.parseInt(this.pcYval);
    },

    pcCoords() {
      return this.maybeData('x', []);
    },

    rowLabels() {
      return this.maybeData('rows', []);
    },

    groupLabels() {
      return this.maybeData('labels', {});
    },

    eigenvalues() {
      return this.maybeData('sdev', []);
    },

    columns() {
      return this.dataset.column.data;
    },

    colors() {
      return this.dataset.groupLevels;
    },
  },

  mounted() {
    console.log(this.dataset);
    console.log(this.plot);
  },

  methods: {
    maybeData(key, dflt) {
      const {
        plot,
      } = this;

      return plot.data ? plot.data[key] : dflt;
    }
  },
};
</script>

<template lang="pug">
vis-tile-large(title="Principal Component Analysis", :loading="plot.loading || false", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title PC selector
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
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

  score-plot(
    v-if="plot.data"
    :pc-x="pcX"
    :pc-y="pcY"
    :show-ellipses="showEllipses"
    :pc-coords="pcCoords"
    :row-labels="rowLabels"
    :colors="colors"
    :group-labels="groupLabels"
    :eigenvalues="eigenvalues"
    :columns="columns"
  )
</template>
