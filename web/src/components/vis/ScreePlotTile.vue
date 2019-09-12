<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScreePlot,
    VisTile,
  },

  props: [
    'width',
    'height',
    'eigenvalues',
  ],

  data() {
    return {
      numComponentsText: '10',
    };
  },

  computed: {
    numComponents() {
      return Number.parseInt(this.numComponentsText, 10);
    },
  }
};
</script>

<template lang="pug">
vis-tile(title="PCA Scree Plot")
  scree-plot(
      :width="width"
      :height="height"
      :eigenvalues="eigenvalues"
      :num-components="numComponents")
  template(v-slot:controls)
    v-menu(bottom, offset-y, left, :min-width="150", :close-on-content-click="false")
      template(v-slot:activator="{ on }")
        v-btn(v-on="on", icon)
          v-icon.mdi.mdi-dots-vertical

      v-card.pa-1(flat)
        v-layout.px-2(column)
          v-text-field.py-2(
              hide-details,
              type="number",
              label="Principal Components",
              min="1",
              outline,
              v-model="numComponentsText")
</template>
