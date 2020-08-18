<script>
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
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
      validator: (prop) => Number.isInteger(prop),
      required: true,
    },

    pcY: {
      type: Number,
      validator: (prop) => Number.isInteger(prop),
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

};
</script>

<template>
  <vis-tile
    title="PLS-DA Loadings Plot"
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
