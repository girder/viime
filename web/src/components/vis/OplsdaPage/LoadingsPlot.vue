<script lang="ts">
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import { defineComponent } from '@vue/composition-api';

export default defineComponent({
  components: {
    LoadingsPlot,
    VisTile,
  },
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
    loadings: {
      type: Array,
      required: true,
    },
  },
});
</script>

<template>
  <vis-tile
    title="OPLS-DA Loadings Plot"
    svg-download
  >
    <loadings-plot
      :points="loadings"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-crosshairs="showCrosshairs"
    />
  </vis-tile>
</template>
