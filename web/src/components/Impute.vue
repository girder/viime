<script>
import { CHANGE_IMPUTATION_OPTIONS } from '../store/actions.type';
import DataTable from './DataTable.vue';
import ToolbarOption from './ToolbarOption.vue';
import {
  mcar_imputation_methods,
  mnar_imputation_methods,
} from '../utils/constants';


export default {
  components: {
    DataTable,
    ToolbarOption,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      mcar_imputation_methods,
      mnar_imputation_methods,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    dataframe() { return this.dataset.measurement_table; },
    ready() { return this.$store.getters.ready(this.id); },
    loading() { return this.$store.state.loading; },

    rowHeaders() {
      return this.dataframe.rowNames.map(text => ({ text, clazz: ['type-key'] }));
    },
    columns() {
      const { columnNames, data, rowNames } = this.dataframe;
      const f = v => (typeof v === 'number' ? v.toFixed(3) : v);

      return columnNames.map((text, j) => ({
        index: j,
        header: { text, clazz: ['type-header'] },
        values: rowNames.map((_, i) => f(data[i][j])),
      }));
    },
  },
  methods: {
    cellClasses() { // rowIndex, columnIndex) {
      // TODO compute if missing
      return ['type-sample'];
    },

    changeImputationSettings(change) {
      this.$store.dispatch(CHANGE_IMPUTATION_OPTIONS, {
        dataset_id: this.id,
        options: {
          mnar: this.dataset.imputationMNAR,
          mcar: this.dataset.imputationMCAR,
          ...change,
        },
      });
    },
  },
};
</script>

<template lang="pug">
v-layout.impute-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      toolbar-option(title="MNAR imputation method", :value="dataset.imputationMNAR",
          @change="changeImputationSettings({mnar: $event})",
          :options="mnar_imputation_methods")
      toolbar-option(title="MCAR imputation method", :value="dataset.imputationMCAR",
          @change="changeImputationSettings({mcar: $event})",
          :options="mcar_imputation_methods")


  v-layout(v-if="!dataset || !ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set

  data-table.impute_table(v-else-if="ready", :row-headers="rowHeaders",
      :columns="columns", :cellClasses="cellClasses")
</template>

<style scoped lang="scss">
.impute-component {
  background: #eee;
}
.impute_table {
  flex: 1 1 0;
}


</style>
