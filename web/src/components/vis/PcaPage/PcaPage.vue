<script>
import ScorePlot from './ScorePlot.vue';
import ScreePlot from './ScreePlot.vue';
import LoadingsPlot from './LoadingsPlot.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';

export default {
  components: {
    ScorePlot,
    ScreePlot,
    LoadingsPlot,
    VisTileLarge,
    LayoutGrid,
  },

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
      showScree: true,
      showScore: true,
      showLoadings: true,
    };
  },

  computed: {
    ready() {
      const pcaReady = this.$store.getters.ready(this.id, 'pca');
      const loadingsReady = this.$store.getters.ready(this.id, 'loadings');

      return pcaReady && loadingsReady;
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
        // eslint-disable-next-line no-restricted-globals
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
vis-tile-large(title="Principal Component Analysis", :loading="false")
  template(#controls)
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

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title.switch-title Scree Plot
        v-switch.switch(v-model="showScree", color="white", hide-details)
    v-card.mb-3.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-text-field.py-2(
              :disabled="!showScree",
              hide-details,
              type="number",
              label="Number of PCs",
              min="1",
              outline,
              v-model="numComponentsVal")
          v-switch.ma-0.py-2(
              v-model="showCutoffs",
              label="Cutoff lines",
              :disabled="!showScree",
              hide-details)

  layout-grid(:cell-size="300", v-if="ready")
    score-plot(
        v-show="showScore",
        :id="id",
        :pc-x="pcX",
        :pc-y="pcY",
        :show-ellipses="showEllipses")
    loadings-plot(
        v-show="showLoadings",
        :id="id",
        :pc-x="pcX",
        :pc-y="pcY",
        :show-crosshairs="showCrosshairs")
    scree-plot(
        v-show="showScree",
        :id="id",
        :pc-x="pcX",
        :pc-y="pcY",
        :num-components="numComponents",
        :show-cutoffs="showCutoffs")
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
