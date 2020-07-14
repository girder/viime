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
      column: [],
      columns: [],
      location: location.href,
      group: '',
      groups: [],
      rocData: {},
      method: 'random_forest',
      methodOptions: [
        { value: 'random_forest', text: 'Random Forest' },
        { value: 'logistic_regression', text: 'Logistic Regression' },
      ],
    };
  },

  watch: {
    column(newColumn) {
      if (!newColumn || newColumn.length === 0) {
        this.rocData = null;
        return;
      }
      this.updateRoc();
    },
    method() {
      this.updateRoc();
    },
    group() {
      this.updateRoc();
    }
  },
  methods: {
    async updateRoc() {
      const id = this.location.split('/')[this.location.split('/').length - 3];
      const apiUrl = new URL('api/v1', process.env.VUE_APP_SERVER_ADDRESS).href;

      const config = {
        method: 'get',
        url: `${apiUrl}/csv/${id}/analyses/roc`,
        params: {
          column: this.column,
          group: this.group,
          method: this.method,
        },
      };
      const unformattedData = (await axios(config)).data;
      this.rocData = unformattedData;
    }
  },
  async mounted() {
    // quick and dirty way to grab file id
    const id = this.location.split('/')[this.location.split('/').length - 3];
    const apiUrl = new URL('api/v1', process.env.VUE_APP_SERVER_ADDRESS).href;
    this.columns = (await axios.get(`${apiUrl}/csv/${id}/analyses/correlation`)).data.columns;
    const groups = (await axios.get(`${apiUrl}/csv/${id}`)).data.group_levels.map((level) => level.name);
    groups.forEach((group) => this.groups.push(group));
    [this.group] = groups;
    [this.column] = this.columns;
  },
};
</script>

<template lang="pug">
vis-tile-large(title="ROC Curve", expanded)
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Metabolite
    v-card.mx-3.px-2(flat)
      v-autocomplete(
          v-model="column",
          :items="columns",
          chips,
          dense,
          deletable-chips,
          auto-select-first,
          hide-selected,
          hide-details,)
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Group
    v-card.mx-3.px-2(flat)
      v-select.py-2(
        hide-details,
        v-model="group",
        :items="groups")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Method
    v-card.mx-3.px-2(flat)
      v-select.py-2(
        hide-details,
        v-model="method",
        :items="methodOptions")
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
