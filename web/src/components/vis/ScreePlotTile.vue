<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScreePlot,
    VisTile,
  },
};
</script>

<template lang="pug">
vis-tile(title="PCA Scree Plot")
  scree-plot(
      :width="600"
      :height="600"
      :variances="[0.6, 0.2, 0.1, 0.05]")
</template>
