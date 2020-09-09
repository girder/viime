<script lang="ts">
import { defineComponent, toRef } from '@vue/composition-api';
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import LoadingsPlotHelp from '../help/LoadingsPlotHelp.vue';
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
  components: {
    LoadingsPlot,
    LoadingsPlotHelp,
    VisTile,
  },
  setup(props) {
    const { plot } = usePlotData(toRef(props, 'id'), 'loadings');
    return { plot };
  },
});
</script>

<template>
  <vis-tile
    title="PCA Loadings Plot"
    :loading="plot.loading"
    svg-download="svg-download"
  >
    <loadings-plot
      :points="plot.data"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-crosshairs="showCrosshairs"
    />
    <template v-slot:help>
      <LoadingsPlotHelp />
    </template>
  </vis-tile>
</template>
