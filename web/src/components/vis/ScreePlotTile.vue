<script>
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import { plotDataMixin } from '../../utils/mixins';

export default {
  components: {
    ScreePlot,
    VisTile,
  },

  mixins: [plotDataMixin('pca')],

  props: {
    width: {
      required: true,
      type: Number,
    },
    height: {
      required: true,
      type: Number,
    },
    id: {
      required: true,
      type: String,
    },
  },

  data() {
    return {
      numComponentsText: '10',
      showCutoffs: true,
    };
  },

  computed: {
    numComponents() {
      return Number.parseInt(this.numComponentsText, 10);
    },
  },
};
</script>

<template lang="pug">
vis-tile(title="PCA Scree Plot")
  scree-plot(
      :width="width",
      :height="height",
      :eigenvalues="plot.data.s",
      :num-components="numComponents",
      :show-cutoffs="showCutoffs")
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
          v-switch.py-2(v-model="showCutoffs", label="Diagnostic cutoffs", hide-details)
</template>
