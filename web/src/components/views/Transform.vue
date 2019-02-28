<script>
import { mapState } from 'vuex';

import { CSVService } from '../../common/api.service';
import { MUTEX_TRANSFORM_TABLE } from '../../store/actions.type';

const normalize_methods = [
  { label: 'None', value: null },
  { label: 'Min Max', value: 'normalize', priority: 10 },
];

const scaling_methods = [
  { label: 'None', value: null },
  { label: 'Autoscaling', value: 'auto_scaling', priority: 200 },
  { label: 'Pareto Scaling', value: 'pareto_scaling', priority: 201 },
  { label: 'Range Scaling', value: 'range_scaling', priority: 202 },
  { label: 'Vast Scaling', value: 'vast_scaling', priority: 203 },
];

const transform_methods = [
  { label: 'None', value: null },
  { label: 'Log 2', value: 'log_2', priority: 100 },
  { label: 'Log 10', value: 'log_10', priority: 101 },
  { label: 'Cube Root', value: 'cube_root', priority: 102 },
];

const all_methods = [
  ...normalize_methods,
  ...scaling_methods,
  ...transform_methods,
];

export default {
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      normalize_methods,
      transform_methods,
      scaling_methods,
    };
  },
  methods: {
    methodFromValue(value) {
      return  all_methods.find(m => m.value === value);
    },
    transformTable(value, category) {
      const method = this.methodFromValue(value);
      this.$store.dispatch(MUTEX_TRANSFORM_TABLE, {
        dataset_id: this.dataset_id,
        transform_type: value,
        args: { priority: method.priority },
        category,
      });
    },
    txTypeOrNull(tx) {
      if (tx && 'transform_type' in tx) return tx.transform_type;
      return null;
    }
  },
  computed: {
    ...mapState({
      norm(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].normalization) },
      trans(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].transformation) },
      scaling(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].scaling) },
    }),
    boxUrl() { return CSVService.getChartUrl(this.dataset_id, 'box'); },
    loadingsUrl() { return CSVService.getChartUrl(this.dataset_id, 'loadings'); },
  },
}
</script>

<template lang="pug">
v-container(fill-height)
  v-layout(row, wrap)
    .cardcontainer
      v-card.pa-3.ma-2
        v-card-title
          h3.headline Normalize
        v-card-actions
          v-radio-group(:value="norm", @change="transformTable($event, 'normalization')")
            v-radio(v-for="m in normalize_methods", :label="m.label",
                :value="m.value", :key="`norm${m.value}`")
        
        v-card-title
          h3.headline Transform
        v-card-actions
          v-radio-group(:value="trans", @change="transformTable($event, 'transformation')")
            v-radio(v-for="m in transform_methods", :label="m.label",
                :value="m.value", :key="`trans${m.value}`")
        
        v-card-title
          h3.headline Scale
        v-card-actions
          v-radio-group(:value="scaling", @change="transformTable($event, 'scaling')")
            v-radio(v-for="m in scaling_methods", :label="m.label",
                :value="m.value", :key="`scale${m.value}`")
    v-layout(row).grow
      v-card.ma-2
        img(:src="`${boxUrl}?cachebust=${norm}${trans}${scaling}`" style="width: 100%;")
</template>
