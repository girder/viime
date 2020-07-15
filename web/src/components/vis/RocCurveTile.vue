<script>
import RocCurve from './RocCurve.vue';
import VisTileLarge from './VisTileLarge.vue';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ToolbarOption,
    VisTileLarge,
    MetaboliteFilter,
    MetaboliteColorer,
    RocCurve,
  },

  mixins: [plotData('roc')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      column: [],
      group: '',
      method: 'random_forest',
      methodOptions: [
        { value: 'random_forest', text: 'Random Forest' },
        { value: 'logistic_regression', text: 'Logistic Regression' },
      ],
    };
  },
  computed: {
    columns() {
      if (this.dataset?.column?.data) {
        return this.dataset.column.data.filter((column) => column.column_type === 'measurement')
          .map((column) => column.column_header);
      }
      return [];
    },
    groups() {
      return this.dataset.groupLevels.map((level) => level.name);
    },
    rocData() {
      if (!this.plot.data) {
        return { sensitivities: [], specificities: [] }
      }
      return {
        sensitivities: this.plot.data.sensitivities,
        specificities: this.plot.data.specificities,
      };
    }
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Group Prediction", :loading="plot.loading", expanded)
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
          hide-details,
          @change="changePlotArgs({column: $event})")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Group
    v-card.mx-3.px-2(flat)
      v-select.py-2(
        hide-details,
        v-model="group",
        :items="groups",
        @change="changePlotArgs({group: $event})")
    v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
      v-toolbar-title Method
    v-card.mx-3.px-2(flat)
      v-select.py-2(
        hide-details,
        v-model="method",
        :items="methodOptions",
        @change="changePlotArgs({method: $event})")
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
