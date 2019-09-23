<script>
import ForceDirectedGraph from './ForceDirectedGraph.vue';
import VisTileLarge from './VisTileLarge.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ForceDirectedGraph,
    VisTileLarge,
  },

  mixins: [plotData('correlation')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  computed: {
    nodes() {
      return !this.plot.data ? []
        : this.plot.data.columns.map(d => ({ id: d }));
    },
    edges() {
      return !this.plot.data ? []
        : this.plot.data.correlations.map(d => ({ source: d.x, target: d.y, value: d.value }));
    },
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Correlation Network", :loading="plot.loading", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Node Color
    v-card.mx-3(flat)
      v-card-actions
        | TODO

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Minimum Correlation
    v-card.mx-3(flat)
      v-card-actions
        | TODO

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Advanced Options
    v-card.mx-3(flat)
      v-card-actions
        | TODO

  template(#default).test
    force-directed-graph(:edges="edges", :nodes="nodes",
        :linkDistance="plot.args.linkDistance", :minValue="plot.args.min_correlation")
</template>
