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

  mixins: [plotData('anova')],

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
vis-tile-large(v-if="plot", title="Anova Table", :loading="plot.loading", expanded)
  anova-table(:data="plot.data")
</template>
