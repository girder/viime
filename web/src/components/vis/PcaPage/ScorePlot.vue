<script lang="ts">
import { defineComponent, toRef } from '@vue/composition-api';
import ScorePlot from '@/components/vis/ScorePlot.vue';
import ScorePlotHelp from '@/components/vis/help/ScorePlotHelp.vue';
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
    showEllipses: {
      type: Boolean,
      required: true,
    },
  },
  components: {
    ScorePlot,
    ScorePlotHelp,
    VisTile,
  },
  setup(props) {
    const { plot, dataset } = usePlotData(toRef(props, 'id'), 'pca');
    return {
      plot,
      dataset,
    };
  },
});
</script>

<template>
  <vis-tile
    title="PCA Score Plot"
    :loading="plot.loading"
    svg-download
  >
    <score-plot
      v-if="plot.data && dataset"
      :pc-coords="plot.data.x"
      :row-labels="plot.data.rows"
      :colors="dataset.groupLevels"
      :group-labels="plot.data.labels"
      :eigenvalues="plot.data.sdev"
      :columns="dataset.column.data"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-ellipses="showEllipses"
    /><template v-slot:help>
      <ScorePlotHelp />
    </template>
  </vis-tile>
</template>
