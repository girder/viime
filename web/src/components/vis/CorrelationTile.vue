<script>
import ForceDirectedGraph from './ForceDirectedGraph.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import plotData from './mixins/plotData';
import { correlation_methods } from './constants';
import { colors } from '../../utils/constants';

export default {
  components: {
    ForceDirectedGraph,
    ToolbarOption,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
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
      colors,
      showNodeLabels: false,
      showEdgeLabels: false,
      linkDistance: 50,
      correlation_methods,
      metaboliteFilter: null,
      metaboliteColor: null,
      search: [], // nodes being searched for
      currentUserInput: '', // the text currently typed in search box
      searchBarResults: new Set(), // current results from autocomplete search box
      excludedSearchBarResults: new Set(),
      highlightedItems: new Set(),
      depthOptions: [
        { value: 0, text: 'Show all' },
        { value: 1, text: 'Show 1' },
        { value: 2, text: 'Show 2' },
        { value: Infinity, text: 'Show reachable' },
      ],
      searchNodeVisibility: 0,
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
      if (!this.plot.data) {
        return [];
      }

      const nodes = this.plot.data.columns.map(d => ({
        id: d,
        color: this.metaboliteColor ? this.metaboliteColor.apply(d) : null,
      }));

      if (!this.metaboliteFilter) {
        return nodes;
      }
      return nodes.filter(n => this.metaboliteFilter.apply(n.id));
    },
    edges() {
      const show = !this.metaboliteFilter ? (() => true) : this.metaboliteFilter.apply;
      return !this.plot.data ? []
        : this.plot.data.correlations
          .filter(d => Math.abs(d.value) > this.min_correlation && show(d.x) && show(d.y))
          .map(d => ({
            source: d.x,
            target: d.y,
            color: d.value < 0 ? colors.negativeCorrelation : colors.positiveCorrelation,
            ori: d.value,
            value: Math.abs(d.value),
          }));
    },
    nodeCount() {
      return this.nodes.length;
    },
    visibleNodes() {
      if (this.search === []) {
        return 0;
      }
      return this.searchNodeVisibility;
    },
  },

  watch: {
    async currentUserInput(newval) {
      if (newval === '') {
        this.highlightedItems = new Set();
      } else {
        await this.$nextTick(); // wait for the filter function to populate the result set
        const highlighted = new Set(this.searchBarResults);
        this.excludedSearchBarResults.forEach(item => highlighted.delete(item));
        this.highlightedItems = highlighted;
      }
    },
  },

  methods: {
    searchFilter(item, queryText, itemText) {
      const match = (itemText
        .toLocaleLowerCase()
        .indexOf(queryText.trim().toLocaleLowerCase()) > -1
      ) && !this.excludedSearchBarResults.has(itemText);
      if (match) {
        this.searchBarResults.add(itemText);
      } else {
        this.searchBarResults.delete(itemText);
      }
      return match;
    },
    clearSearch() {
      this.search = [];
      this.currentUserInput = ''; // clear search box
      this.searchBarResults = new Set(); // unhighlight search result nodes
    },
    clearExcludedNodes() {
      this.excludedSearchBarResults = new Set();
    },
    removeNodeFromSearchResults(event, data) {
      this.excludedSearchBarResults = new Set([...this.excludedSearchBarResults, data.item]);
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
    metabolite-filter(title="Node Filter", :dataset="dataset", v-model="metaboliteFilter",
        :not-selected-color="colors.correlationNode", selection-last)
    //- metabolite-colorer(title="Node Color", :dataset="dataset", v-model="metaboliteColor",
    //-     :not-selected-color="colors.correlationNode", selection-last)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Search
    v-card.mx-3.px-2(flat)
      div
        v-autocomplete(
            v-model="search",
            :search-input.sync="currentUserInput",
            :items="nodes.map(node => node.id)\
                    .filter(node => !excludedSearchBarResults.has(node))",
            chips,
            multiple,
            dense,
            deletable-chips,
            auto-select-first,
            hide-selected,
            hide-details,
            :filter="searchFilter")
          template(v-slot:item="data")
            v-chip(smal)
              v-icon.closePillButton.pr-2(@click.stop="removeNodeFromSearchResults($event, data)")
                | mdi-eye-off
              span {{ data.item }}
      v-btn.my-0.mx-0.mt-2(small, flat, @click="clearSearch")
        v-icon.pr-2 mdi-close
        | Clear Selections
      v-btn.my-0.mx-0(small, flat,
          @click="clearExcludedNodes",
          :disabled="excludedSearchBarResults.size === 0")
        v-icon.pr-2 mdi-eye
        | Unhide Nodes
      v-select.py-2(
          hide-details,
          v-model="searchNodeVisibility",
          :disabled="search.length === 0",
          :items="depthOptions")

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
    force-directed-graph(:edges="edges",
        :nodes="nodes",
        :link-distance="linkDistanceAsNumber",
        :show-node-labels="showNodeLabels",
        :show-edge-labels="showEdgeLabels",
        :min-stroke-value="min_correlation",
        :search="search",
        :highlighted-items="highlightedItems",
        :excluded-items="excludedSearchBarResults",
        :visible-nodes="visibleNodes")
</template>

<style scoped>
.closePillButton:hover {
  color: red;
}

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
