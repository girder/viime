<script lang="ts">
import { defineComponent, computed } from '@vue/composition-api';
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
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
    showCrosshairs: {
      type: Boolean,
      required: true,
    },
  },
  components: { LoadingsPlot, VisTile },
  setup(props) {
    // TODO this won't be necessary in Vue 3
    const id = computed(() => props.id);
    const { plot } = usePlotData(id, 'loadings');
    return { plot };
  },
});
</script>

<template lang="pug">
vis-tile(title="PCA Loadings Plot", :loading="plot.loading", svg-download)
  loadings-plot(
      :points="plot.data",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-crosshairs="showCrosshairs")
  template(v-slot:help)
    include ../help/LoadingsPlotHelp.pug
</template>
