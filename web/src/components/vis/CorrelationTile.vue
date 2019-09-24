<script>
import ForceDirectedGraph from './ForceDirectedGraph.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';
import { correlation_methods } from './constants';

export default {
  components: {
    ForceDirectedGraph,
    ToolbarOption,
    VisTileLarge,
  },

  mixins: [plotData('correlation')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      showLabels: false,
      linkDistance: 50,
      correlation_methods,
    };
  },

  computed: {
    min_correlation() {
      return this.plot.args.min_correlation;
    },
    linkDistanceAsNumber() {
      return parseInt(this.linkDistance, 10);
    },
    nodes() {
      return !this.plot.data ? []
        : this.plot.data.columns
          .map(d => ({ id: d }));
    },
    edges() {
      return !this.plot.data ? []
        : this.plot.data.correlations
          .filter(d => d.value > this.min_correlation)
          .map(d => ({ source: d.x, target: d.y, value: Math.abs(d.value) }));
    },
  },

};
</script>

<template lang="pug">
vis-tile-large.correlation(v-if="plot", title="Correlation Network", :loading="plot.loading",
    expanded)
  template(#controls)
    toolbar-option(title="Method", :value="plot.args.method",
        :options="correlation_methods",
        @change="changePlotArgs({method: $event})")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Minimum Correlation
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.minCorrelation(:value="min_correlation", label="0", thumb-label,
              hide-details, min="0", max="1", step="0.01",
              @change="changePlotArgs({min_correlation: $event})")

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Advanced Options
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch(v-model="showLabels", label="Node Labels")
          v-text-field(v-model="linkDistance", label="Link Distance",
              hide-details, min="0", max="100", step="10", type="number")

  template(#default)
    force-directed-graph(:edges="edges", :nodes="nodes",
        :link-distance="linkDistanceAsNumber", :show-labels="showLabels")
</template>

<style scoped>
.minCorrelation >>> .v-input__slot::after {
  content: "1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
