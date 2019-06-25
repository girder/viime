<script>
import { MUTEX_TRANSFORM_TABLE, LOAD_PLOT } from '@/store/actions.type';
import {
  normalize_methods,
  scaling_methods,
  transform_methods,
} from '@/utils/constants';
import VisPca from '@/components/vis/VisPca.vue';
import VisLoadings from '@/components/vis/VisLoadings.vue';

export default {
  components: {
    VisPca,
    VisLoadings,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      normalize_methods,
      transform_methods,
      scaling_methods,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    loading() { return this.$store.state.loading; },
    norm() { return this.$store.getters.txType(this.id, 'normalization'); },
    trans() { return this.$store.getters.txType(this.id, 'transformation'); },
    scaling() { return this.$store.getters.txType(this.id, 'scaling'); },
    pcaData() { return this.$store.getters.plotData(this.id, 'pca'); },
    pcaValid() { return this.$store.getters.plotValid(this.id, 'pca'); },
    loadingsData() { return this.$store.getters.plotData(this.id, 'loadings'); },
    loadingsValid() { return this.$store.getters.plotValid(this.id, 'loadings'); },
  },
  watch: {
    pcaValid: {
      immediate: true,
      handler(valid) {
        if (valid === false) {
          this.$store.dispatch(LOAD_PLOT, { dataset_id: this.id, name: 'pca' });
        }
      },
    },
    loadingsValid: {
      immediate: true,
      handler(valid) {
        if (valid === false) {
          this.$store.dispatch(LOAD_PLOT, { dataset_id: this.id, name: 'loadings' });
        }
      },
    },
  },
  methods: {
    async transformTable(value, category) {
      this.$store.dispatch(MUTEX_TRANSFORM_TABLE, {
        dataset_id: this.id,
        transform_type: value,
        category,
      });
    },
  },
};
</script>

<template lang="pug">
v-layout.transform-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset")
      v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
        v-toolbar-title Normalize
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:value="norm", @change="transformTable($event, 'normalization')")
            v-radio(v-for="m in normalize_methods", :label="m.label",
                :value="m.value", :key="`norm${m.value}`")

      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Transform
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:value="trans", @change="transformTable($event, 'transformation')")
            v-radio(v-for="m in transform_methods", :label="m.label",
                :value="m.value", :key="`trans${m.value}`")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Scale
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:value="scaling", @change="transformTable($event, 'scaling')")
            v-radio(v-for="m in scaling_methods", :label="m.label",
                :value="m.value", :key="`scale${m.value}`")

  v-layout(v-if="!dataset", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
  v-container.overflow-auto(v-else)
    v-layout(row, fill-height, ref="contentarea")
      .pa-4
        h3.headline.ml-5 PCA Scores
        vis-pca(:width="800", :height="600", :raw-points="pcaData", :dataset="dataset")
    v-layout(row, fill-height, ref="contentarea")
      .pa-4
        h3.headline.ml-5 PCA Loadings
        vis-loadings(:width="800", :height="600", :points="loadingsData")
</template>
