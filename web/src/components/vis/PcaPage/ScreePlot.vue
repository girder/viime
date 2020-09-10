<script lang="ts">
import { defineComponent, toRef } from '@vue/composition-api';
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import usePlotData from '../use/usePlotData';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
    pcX: {
      type: Number,
      required: true,
    },
    pcY: {
      type: Number,
      required: true,
    },
    numComponents: {
      type: Number,
      validator: (prop: number) => Number.isInteger(prop) && prop > 0,
      required: true,
    },
    showCutoffs: {
      type: Boolean,
      required: true,
    },
  },
  components: { ScreePlot, VisTile },
  setup(props) {
    const { plot } = usePlotData(toRef(props, 'id'), 'pca');
    return { plot };
  },
});
</script>

<template lang="pug">
vis-tile(title="PCA Scree Plot", :loading="plot.loading", svg-download)
  scree-plot(
      v-if="plot.data",
      :eigenvalues="plot.data.sdev",
      :pc-x="pcX",
      :pc-y="pcY",
      :num-components="numComponents",
      :show-cutoffs="showCutoffs")
  template(v-slot:help)
    include ../help/ScreePlotHelp.pug
</template>
