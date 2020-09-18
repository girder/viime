<script lang="ts">
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import { defineComponent } from '@vue/composition-api';

export default defineComponent({
  components: {
    ScorePlot,
    VisTile,
  },
  props: {
    pcX: {
      type: Number,
      required: true,
    },
    pcY: {
      type: Number,
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
});
</script>

<template>
  <vis-tile
    title="OPLS-DA Score Plot"
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
