<script>
import AnovaTable from '@/components/vis/AnovaTable.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    AnovaTable,
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
};
</script>

<template lang="pug">
vis-tile-large(title="Anova Table", :loading="plot.loading", expanded)
  anova-table(
      :width="width",
      :height="height",
      :data="plot.data")
</template>
