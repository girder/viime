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
      excludedSearchBarResults: [],
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
    searchResults() {
      // if input is empty, don't highlight any nodes
      if (!this.currentUserInput || this.currentUserInput.trim() === '') {
        return [];
      }
      return Array.from(this.searchBarResults);
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
  methods: {
    searchFilter(item, queryText, itemText) {
      const match = itemText.toLocaleLowerCase().indexOf(queryText.trim().toLocaleLowerCase()) > -1
                    && !this.excludedSearchBarResults.includes(itemText);
      if (match) {
        this.searchBarResults.add(itemText);
      } else {
        this.searchBarResults.delete(itemText);
      }
      return match;
    },
    clearSearch(event) {
      event.preventDefault();
      this.search = [];
      this.currentUserInput = ''; // clear search box
      this.searchBarResults = new Set(); // unhighlight search result nodes
    },
    clearExcludedNodes() {
      this.excludedSearchBarResults = [];
    },
    removeNodeFromSearchResults(event, data) {
      event.stopPropagation();
      this.excludedSearchBarResults.push(data.item);
      // add char to search box to trigger rerender
      // of search results.
      // TODO: find better way to do this
      if (!this.currentUserInput) {
        this.currentUserInput = '';
      }
      this.currentUserInput = this.currentUserInput.concat('\n');
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
    metabolite-colorer(title="Node Color", :dataset="dataset", v-model="metaboliteColor",
        :not-selected-color="colors.correlationNode", selection-last)

    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Search
    v-card.mx-3(flat)
      span.searchBarContainers
        v-autocomplete.searchBar(v-model="search",
            :search-input.sync="currentUserInput",
            :items="nodes.map(node => node.id)\
                    .filter(node => !excludedSearchBarResults.includes(node))",
            chips,
            multiple,
            deletable-chips,
            auto-select-first,
            hide-selected,
            :filter="searchFilter",
            @change="clearSearch")
          template(v-slot:item="data")
            v-chip
              v-icon.closePillButton(v-text="'mdi-alpha-x-circle'",
                  style="margin-right: 12px; float: right;",
                  @click="(e) => removeNodeFromSearchResults(e, data)")
              span(v-text="data.item")
      span.searchBarContainers
        v-icon(@click="(e) => clearSearch(e)", v-text="'mdi-delete'")
      v-btn.searchBarContainers(v-text="'Unhide Nodes'",
      @click="clearExcludedNodes",
      :disabled="excludedSearchBarResults.length === 0")

      v-radio-group(v-model="searchNodeVisibility",
          :disabled="search.length === 0")
        v-radio(:label="'Show all'",
            :value="0")
        v-radio(:label="'Show within 1 step'",
            :value="1")
        v-radio(:label="'Show within 2 steps'",
            :value="2")
        v-radio(:label="'Show all reachable'",
            :value="Infinity")

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
        :filtered-items="searchResults.filter(node => !excludedSearchBarResults.has(node))",
        :excluded-search-results="excludedSearchBarResults",
        :visible-nodes="visibleNodes")
</template>

<style scoped>

.closePillButton:hover {
  color: red;
}

.searchBarContainers {
  display: inline-block;
  margin-left: 1em;
}

.searchBar {
  max-width: 100px;
  overflow: auto;
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
