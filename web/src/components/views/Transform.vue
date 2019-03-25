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
import HeaderFooterContainer from '@/components/containers/HeaderFooter.vue';
import SaveStatus from '@/components/SaveStatus.vue';
import Stepper from '@/components/stepper/Stepper.vue';

const all_methods = [
  ...normalize_methods,
  ...scaling_methods,
  ...transform_methods,
];

export default {
  components: {
    HeaderFooterContainer,
    SaveStatus,
    VisPca,
    Stepper,
  },
  mixins: [loadDataset],
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      normalize_methods,
      transform_methods,
      scaling_methods,
      pcaPoints: {
        x: [],
      },
      stepperCollapsed: false,
      stepperModel: 2,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.dataset_id); },
    loading() { return this.$store.state.loading; },
    norm() { return this.$store.getters.txType(this.dataset_id, 'normalization'); },
    normEnabled() { return this.dataset.normalization.enabled; },
    trans() { return this.$store.getters.txType(this.dataset_id, 'transformation'); },
    transEnabled() { return this.dataset.transformation.enabled; },
    scaling() { return this.$store.getters.txType(this.dataset_id, 'scaling'); },
    scalingEnabled() { return this.dataset.scaling.enabled; },
    transformed() { return this.dataset && this.dataset.transformed; },
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
      const method = this.methodFromValue(txtype);
      this.$store.dispatch(MUTEX_TRANSFORM_TABLE, {
        dataset_id: this.dataset_id,
        transform_type: txtype,
        args: { priority: method.priority },
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
header-footer-container.transform-view
  template(#header)
      stepper(v-model="stepperModel", :collapsed.sync="stepperCollapsed")

  v-layout(row, fill-height, justify-center, align-center, ref="contentarea")
    div
      h3.headline.ml-5 Principal Component Analysis
      vis-pca(:width="800", :height="600", :raw-points="pcaPoints")

  template(#footer)
    v-layout(row, wrap, grow, v-if="dataset")

      v-card.transform-container.grow(flat)
        v-toolbar.darken-3(color="secondary", dark, flat, dense, :card="false")
          v-toolbar-title Normalize
          v-spacer
          v-switch.shrink(hide-details, :input-value="normEnabled",
              @change="transformTable($event, 'normalization')", :disabled="loading")
        v-card-actions.pl-3
          v-radio-group(:disabled="!normEnabled || loading", :value="norm",
              @change="transformTable($event, 'normalization')")
            v-radio(v-for="m in normalize_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`norm${m.value}`")

      v-card.transform-container.grow(flat)
        v-toolbar.darken-3(color="secondary", dark, flat, dense, :card="false")
          v-toolbar-title Transform
          v-spacer
          v-switch.shrink(hide-details, :input-value="transEnabled",
              @change="transformTable($event, 'transformation')", :disabled="true")
        v-card-actions.pl-3
          v-radio-group(:disabled="!transEnabled || loading", :value="trans",
              @change="transformTable($event, 'transformation')")
            v-radio(v-for="m in transform_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`trans${m.value}`")

      v-card.transform-container.grow(flat)
        v-toolbar.darken-3(color="secondary", dark, flat, dense)
          v-toolbar-title Scale
          v-spacer
          v-switch.shrink(hide-details, :input-value="scalingEnabled",
              @change="transformTable($event, 'scaling')", :disabled="true")
        v-card-actions.pl-3
          v-radio-group(:disabled="!scalingEnabled || loading", :value="scaling",
              @change="transformTable($event, 'scaling')")
            v-radio(v-for="m in scaling_methods", :label="m.label",
                v-if="m.value", :value="m.value", :key="`scale${m.value}`")

    v-toolbar.footer(flat, dense)
      v-btn(depressed, color="accent", :to="`/cleanup/${dataset_id}`")
        v-icon.pr-1 {{ $vuetify.icons.arrowLeft }}
        | Go Back
      v-spacer
      save-status
      v-spacer
      v-btn(depressed, disabled)
        | Continue
        v-icon.pl-1 {{ $vuetify.icons.arrowRight }}
</template>

<style lang="scss">
.transform-view {
  .transform-container {
    &>.v-toolbar {
      border-top-left-radius: 0 !important;
      border-top-right-radius: 0 !important;
    }

    &:nth-child(odd) {
      background-color: #eeeeee;
    }

    &:nth-child(even) {
      background-color: #e6e6e6;
      .v-toolbar {
        background-color: #222d32 !important;
      }
    }
  }
}
</style>
