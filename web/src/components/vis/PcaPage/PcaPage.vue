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
      showEllipses: true,
      showCrosshairs: true,
      showCutoffs: true,
      showScree: true,
      showScore: true,
      showLoadings: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval);
    },

    pcY() {
      return Number.parseInt(this.pcYval);
    },

    numComponents() {
      return Number.parseInt(this.numComponentsVal);
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(title="Principal Component Analysis", :loading="false", expanded)
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
              :disabled="!showScore && !showLoadings"
              v-model="pcXval")
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              outline,
              :disabled="!showScore && !showLoadings"
              v-model="pcYval")


    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title
        v-container(pa-0 fluid)
          v-layout(align-center)
            v-flex Scree Plot
            v-flex
              v-switch.py-2(v-model="showScree", color="white", hide-details)
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-text-field.py-2(
              :disabled="!showScree"
              hide-details,
              type="number",
              label="Number of PCs",
              min="1",
              outline,
              v-model="numComponentsVal")
          v-switch.py-2(
            v-model="showCutoffs"
            label="Cutoff lines"
            :disabled="!showScree"
            hide-details)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title
        v-container(pa-0 fluid)
          v-layout(align-center)
            v-flex Score Plot
            v-flex
              v-switch.py-2(v-model="showScore", color="white", hide-details)
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch.py-2(
            v-model="showEllipses"
            label="Data ellipses"
            :disabled="!showScore"
            hide-details)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title
        v-container(pa-0 fluid)
          v-layout(align-center)
            v-flex Loadings Plot
            v-flex
              v-switch.py-2(v-model="showLoadings", color="white", hide-details)
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch.py-2(
            v-model="showCrosshairs"
            label="Crosshairs"
            :disabled="!showLoadings"
            hide-details)

  v-container.grow-overflow.ma-0(grid-list-lg, fluid)
    layout-grid(:cell-size="300")
      scree-plot(
        v-show="showScree"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :num-components="numComponents"
        :show-cutoffs="showCutoffs")
      score-plot(
        v-show="showScore"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :show-ellipses="showEllipses")
      loadings-plot(
        v-show="showLoadings"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :show-crosshairs="showCrosshairs")
</template>
