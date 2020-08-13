<script>
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';
import ScorePlot from './ScorePlot.vue';
import LoadingsPlot from './LoadingsPlot.vue';
import plotData from '../mixins/plotData';

export default {
  components: {
    ScorePlot,
    LoadingsPlot,
    VisTileLarge,
    LayoutGrid,
  },

  mixins: [plotData('plsda')],

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
      numComponentsVal: '10',
      pcX: 1,
      pcY: 2,
      numComponents: 10,
      showEllipses: true,
      showCrosshairs: true,
      showCutoffs: true,
      showScore: true,
      showLoadings: true,
    };
  },

  computed: {
    ready() {
      const pcaReady = this.$store.getters.ready(this.id, 'plsda_scores');
      const loadingsReady = this.$store.getters.ready(this.id, 'plsda_loadings');
      return pcaReady && loadingsReady;
    },
    loadings() {
      if (this.plot?.data?.loadings) {
        return this.plot.data.loadings;
      }
      return [];
    },
    pcCoords() {
      if (this.plot?.data?.scores?.x) {
        return this.plot.data.scores.x;
      }
      return [];
    },
    eigenvalues() {
      if (this.plot?.data?.scores?.sdev) {
        return this.plot.data.scores.sdev;
      }
      return [];
    },
    rowLabels() {
      if (this.dataset?.row?.data) {
        return this.dataset.row.data.filter((row) => row.row_type === 'sample').map((row) => row.row_name);
      }
      return [];
    },
    groupLabels() {
      if (this.dataset?.validatedGroups?.data) {
        const groupColumnName = this.dataset.validatedGroups.columnNames[0];
        const groupLabels = {};
        groupLabels[groupColumnName] = this.dataset.validatedGroups.data.map((group) => group);
        return groupLabels;
      }
      return {};
    },
    columns() {
      if (this.dataset?.column?.data) {
        return this.dataset.column.data;
      }
      return [];
    },

    groupLevels() {
      if (this.dataset?.groupLevels) {
        return this.dataset.groupLevels;
      }
      return [];
    },
  },
  watch: {
    pcXval: {
      handler(val) {
        const pcX = Number.parseInt(val, 10);
        if (!Number.isNaN(pcX)) {
          this.pcX = pcX;
        }
      },
      immediate: true,
    },
    pcYval: {
      handler(val) {
        const pcY = Number.parseInt(val, 10);
        if (!Number.isNaN(pcY)) {
          this.pcY = pcY;
        }
      },
      immediate: true,
    },
    numComponentsVal: {
      handler(val) {
        const numComponents = Number.parseInt(val, 10);
        if (!Number.isNaN(numComponents)) {
          this.numComponents = numComponents;
        }
      },
      immediate: true,
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(title="Partial Least Squares Discriminant Analysis", :loading="plot.loading")
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Components
    v-card.mb-3.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-text-field.py-2(
              hide-details,
              type="number",
              min="1",
              outline,
              :disabled="plot.loading"
              label="Number of Components",
              @change="changePlotArgs({ num_of_components: $event });"
              v-model="numComponentsVal")

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title PC selector
    v-card.mb-3.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (X Axis)",
              min="1",
              outline,
              :disabled="!showScore && !showLoadings",
              v-model="pcXval")
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              outline,
              :disabled="!showScore && !showLoadings",
              v-model="pcYval")

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title.switch-title Score Plot
        v-switch.switch(v-model="showScore", color="white", hide-details)
    v-card.mb-3.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch.ma-0.py-2(
              v-model="showEllipses",
              label="Data ellipses",
              :disabled="!showScore",
              hide-details)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title.switch-title Loadings Plot
        v-switch.switch(v-model="showLoadings", color="white", hide-details)
    v-card.mb-3.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch.ma-0.py-2(
              v-model="showCrosshairs",
              label="Crosshairs",
              :disabled="!showLoadings",
              hide-details)

  layout-grid(:cell-size="300", v-if="ready")
    score-plot(
        v-show="showScore",
        :id="id",
        :pc-x="pcX",
        :pc-y="pcY",
        :show-ellipses="showEllipses",
        :pc-coords="pcCoords",
        :row-labels="rowLabels",
        :columns="columns",
        :eigenvalues="eigenvalues",
        :group-labels="groupLabels",
        :group-levels="groupLevels")
    loadings-plot(
        v-show="showLoadings",
        :id="id",
        :pc-x="pcX",
        :pc-y="pcY",
        :show-crosshairs="showCrosshairs",
        :loadings="loadings")
  div(v-else)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading data...
</template>

<style lang="scss" scoped>
.switch-title {
  align-items: center;
  display: flex;
  justify-content: space-between;
  overflow: visible;
  width: 100%;
  .switch {
    flex-grow: 0;
    margin-right: -10px;
  }
}
</style>
