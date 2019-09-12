<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScreePlot,
    VisTile,
  },

  props: ScreePlot.props,
};
</script>

<template lang="pug">
vis-tile(title="PCA Scree Plot")
  scree-plot(
      :width="width"
      :height="height"
      :eigenvalues="eigenvalues")
</template>
