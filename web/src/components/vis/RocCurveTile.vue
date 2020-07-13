<script>
import { csvFormat } from 'd3-dsv';
import axios from 'axios';
import RocCurve from './RocCurve.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import plotData from './mixins/plotData';
import { SET_DATASET_SELECTED_COLUMNS } from '../../store/actions.type';
import { downloadCSV } from '../../utils/exporter';

export default {
  components: {
    ToolbarOption,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
    RocCurve,
  },

  props: {

  },

  data() {
    return {
      search: [],
      currentUserInput: '',
      columns: [],
      location: location.href,
      groups: [],
      rocData: {},
    };
  },

  watch: {
    async search(newSearch) {
      if (!newSearch || newSearch.length === 0) {
        this.rocData = null;
        return;
      }
      const id = this.location.split('/')[this.location.split('/').length - 3];
      const apiUrl = new URL('api/v1', process.env.VUE_APP_SERVER_ADDRESS).href;

      const config = {
        method: 'get',
        url: `${apiUrl}/csv/${id}/analyses/roc`,
        params: {
          column: newSearch,
          group: this.groups[0],
          method: 'random_forest', // TODO
        },
      };
      const unformattedData = (await axios(config)).data;
      this.rocData = unformattedData;
    },
  },

  async mounted() {
    // quick and dirty way to grab file id
    const id = this.location.split('/')[this.location.split('/').length - 3];
    const apiUrl = new URL('api/v1', process.env.VUE_APP_SERVER_ADDRESS).href;
    this.columns = (await axios.get(`${apiUrl}/csv/${id}/column`)).data;
    const groups = (await axios.get(`${apiUrl}/csv/${id}`)).data.group_levels.map((level) => level.name);
    groups.forEach((group) => this.groups.push(group));
  },
};
</script>

<template lang="pug">
vis-tile-large(title="ROC Curve", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Metabolite
    v-card.mx-3.px-2(flat)
      div
        v-autocomplete(
            v-model="search",
            :search-input.sync="currentUserInput",
            :items="columns.filter(column => column.column_type === 'measurement').map(column => column.column_header)",
            chips,
            dense,
            deletable-chips,
            auto-select-first,
            hide-selected,
            hide-details,)
  roc-curve(:roc-data="rocData")
</template>

<style>
.horizontalScrollable {
  position: absolute;
}

.minCorrelation {
  padding-top: 16px;
}

.minCorrelation >>> .v-input__slot::after {
  content: "0.1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
