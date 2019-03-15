<script>
import { mapState } from 'vuex';

import { CSVService } from '../../common/api.service';
import { MUTEX_TRANSFORM_TABLE } from '../../store/actions.type';
import VisPca from '@/components/vis/VisPca.vue';

import { loadDataset } from '@/utils/mixins';

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
  mixins: [loadDataset],
  components: {
    VisPca,
  },
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      normalize_methods,
      transform_methods,
      scaling_methods,
      points: [],
    };
  },
  computed: {
    ...mapState({
      norm(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].normalization); },
      trans(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].transformation); },
      scaling(state) { return this.txTypeOrNull(state.datasets[this.dataset_id].scaling); },
      transformed(state) { return state.datasets[this.dataset_id].transformed; },
    }),
    boxUrl() { return CSVService.getChartUrl(this.dataset_id, 'box'); },
  },
  watch: {
    transformed() {
      this.loadPCAData(this.dataset_id);
    },
  },
  mounted() {
    this.loadPCAData(this.dataset_id);
  },
  methods: {
    methodFromValue(value) {
      return all_methods.find(m => m.value === value);
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
    },
    async loadPCAData(csv) {
      const pcaData = await CSVService.getPlot(csv, 'pca');
      this.points = pcaData.data;
    },
  },

};
</script>

<template lang="pug">
v-container(fill-height)
  v-layout(row, wrap, align-content-start)
    .cardcontainer.grow.pa-2
      v-card.pa-3
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
    v-layout.pa-2(column)
      v-card
        vis-pca(:width="500", :height="400", :points="points")
</template>
