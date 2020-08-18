<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  props: {
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

    showEllipses: {
      type: Boolean,
      required: true,
    },

    pcCoords: {
      type: Array,
      required: true,
    },

    rowLabels: {
      type: Array,
      required: true,
    },

    groupLabels: {
      type: Object,
      required: true,
    },

    groupLevels: {
      type: Array,
      required: true,
    },

    eigenvalues: {
      type: Array,
      required: true,
    },

    columns: {
      type: Array,
      required: true,
    },
  },
};
</script>

<template>
  <vis-tile
    title="PLS-DA Score Plot"
    svg-download
  >
    <score-plot
      :pc-coords="pcCoords"
      :row-labels="rowLabels"
      :colors="groupLevels"
      :group-labels="groupLabels"
      :eigenvalues="eigenvalues"
      :columns="columns"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-ellipses="showEllipses"
    />
  </vis-tile>
</template>
