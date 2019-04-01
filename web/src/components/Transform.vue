<script>
import { CSVService } from '@/common/api.service';
import { MUTEX_TRANSFORM_TABLE } from '@/store/actions.type';
import {
  normalize_methods,
  scaling_methods,
  transform_methods,
} from '@/utils/constants';
import { loadDataset } from '@/utils/mixins';
import VisPca from '@/components/vis/VisPca.vue';

export default {
  components: {
    VisPca,
  },
  mixins: [loadDataset],
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
      pcaPoints: {
        x: [],
      },
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    loading() { return this.$store.state.loading; },
    norm() { return this.$store.getters.txType(this.id, 'normalization'); },
    trans() { return this.$store.getters.txType(this.id, 'transformation'); },
    scaling() { return this.$store.getters.txType(this.id, 'scaling'); },
    transformed() { return this.dataset && this.dataset.transformed; },
  },
  watch: {
    transformed() {
      this.loadPCAData(this.id);
    },
  },
  mounted() {
    this.loadPCAData(this.id);
  },
  methods: {
    async transformTable(value, category) {
      let txtype = value;
      if (value === false) {
        txtype = null;
      } else if (value === true) {
        switch (category) {
          case 'normalization':
            txtype = normalize_methods[0].value; break;
          case 'transformation':
            txtype = transform_methods[0].value; break;
          case 'scaling':
            txtype = scaling_methods[0].value; break;
          default:
            throw new Error(`${category} is not valid.`);
        }
      }
      this.$store.dispatch(MUTEX_TRANSFORM_TABLE, {
        id: this.id,
        transform_type: txtype,
        category,
      });
    },
    async loadPCAData(csv) {
      const pcaData = await CSVService.getPlot(csv, 'pca');
      this.pcaPoints = pcaData.data;
    },
  },
};
</script>

<template lang="pug">
v-layout.transform-view(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset")
      v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
        v-toolbar-title Normalize
        v-spacer
        v-switch.shrink(hide-details, :input-value="norm",
            @change="transformTable($event, 'normalization')", :disabled="loading")
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:disabled="!norm || loading", :value="norm",
              @change="transformTable($event, 'normalization')")
            v-radio(v-for="m in normalize_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`norm${m.value}`")

      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Transform
        v-spacer
        v-switch.shrink(hide-details, :input-value="trans",
            @change="transformTable($event, 'transformation')", :disabled="true")
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:disabled="!trans || loading", :value="trans",
              @change="transformTable($event, 'transformation')")
            v-radio(v-for="m in transform_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`trans${m.value}`")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Scale
        v-spacer
        v-switch.shrink(hide-details, :input-value="scaling",
            @change="transformTable($event, 'scaling')", :disabled="true")
      v-card.ma-3(flat)
        v-card-actions
          v-radio-group(:disabled="!scaling || loading", :value="scaling",
              @change="transformTable($event, 'scaling')")
            v-radio(v-for="m in scaling_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`scale${m.value}`")
  v-layout(row, fill-height, ref="contentarea")
    .pa-4
      h3.headline.ml-5 Principal Component Analysis
      vis-pca(:width="800", :height="600", :raw-points="pcaPoints")
</template>
