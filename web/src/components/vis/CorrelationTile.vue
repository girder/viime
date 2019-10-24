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
      showNodeLabels: false,
      showEdgeLabels: false,
      linkDistance: 50,
      correlation_methods,
      showSelected: true,
      showNotSelected: true,
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
      const selected = new Set(this.dataset.selectedColumns || []);
      const { showSelected, showNotSelected } = this;
      return !this.plot.data ? []
        : this.plot.data.columns
          .map(d => ({
            id: d,
            highlighted: selected.has(d),
          })).filter(d => (d.highlighted ? showSelected : showNotSelected));
    },
    edges() {
      const selected = new Set(this.dataset.selectedColumns || []);
      const { showSelected, showNotSelected } = this;
      const show = id => (selected.has(id) ? showSelected : showNotSelected);
      return !this.plot.data ? []
        : this.plot.data.correlations
          .filter(d => Math.abs(d.value) > this.min_correlation && show(d.x) && show(d.y))
          .map(d => ({
            source: d.x,
            target: d.y,
            value: Math.abs(d.value),
          }));
    },
    countSelected() {
      return (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.plot.data) {
        return 0;
      }
      return this.plot.data.columns.length - this.countSelected;
    },
  },
};
</script>

<template lang="pug">
vis-tile-large.correlation(v-if="plot", title="Correlation Network", :loading="plot.loading",
    expanded, download)
  template(#controls)
    toolbar-option(title="Method", :value="plot.args.method",
        :options="correlation_methods",
        @change="changePlotArgs({method: $event})")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Minimum Correlation
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-slider.my-1.minCorrelation(:value="min_correlation", label="0", thumb-label="always",
              hide-details, min="0", max="1", step="0.01",
              @change="changePlotArgs({min_correlation: $event})")
    v-toolbar.darken-3(color="primary", dark, flat, dense)
      v-toolbar-title Node Filter
    v-card.mx-3(flat)
      v-card-actions.checkboxlist
        v-checkbox.my-0(v-model="showSelected", :label="`Selected (${countSelected})`",
            hide-details, color="#ffa500")
        v-checkbox.my-0(v-model="showNotSelected", :label="`Not Selected (${countNotSelected})`",
            hide-details, color="#4682b4")

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Advanced Options
    v-card.mx-3(flat)
      v-card-actions
        v-layout(column)
          v-switch.my-1(v-model="showNodeLabels", label="Node Labels", hide-details)
          v-switch.my-1(v-model="showEdgeLabels", label="Edge Labels", hide-details)
          v-text-field.my-1(v-model="linkDistance", label="Link Distance",
              hide-details, min="0", step="10", type="number")

  template(#default)
    force-directed-graph(:edges="edges", :nodes="nodes",
        :link-distance="linkDistanceAsNumber", :show-node-labels="showNodeLabels",
        :show-edge-labels="showEdgeLabels",
        :min-stroke-value="min_correlation", highlight-color="#ffa500", color="#4682b4")
</template>

<style scoped>

.minCorrelation {
  padding-top: 16px;
}

.minCorrelation >>> .v-input__slot::after {
  content: "1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}

.checkboxlist {
  display: block;
}

</style>
