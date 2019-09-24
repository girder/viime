<script>
import WilcoxonPlot from '@/components/vis/WilcoxonPlot.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    WilcoxonPlot,
    ToolbarOption,
    VisTileLarge,
  },

  mixins: [plotData('wilcoxon')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      threshold: 0.05,
    };
  },
};
</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Wilcoxon Test", :loading="plot.loading", expanded)
  wilcoxon-plot(:data="plot.data")
</template>
