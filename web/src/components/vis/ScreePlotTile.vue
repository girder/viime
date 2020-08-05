<script lang="ts">
import { defineComponent, computed, ref } from '@vue/composition-api';
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import usePlotData from './use/usePlotData';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },

  components: { ScreePlot, VisTile },

  setup(props) {
    // TODO this won't be necessary in Vue 3
    const id = computed(() => props.id);
    const showCutoffs = ref(true);
    const numComponentsText = ref('10');
    const numComponents = computed(() => Number.parseInt(numComponentsText.value, 10));

    const { plot } = usePlotData(id, 'pca');

    return {
      numComponentsText,
      numComponents,
      showCutoffs,
      plot,
    };
  },
});
</script>

<template lang="pug">
vis-tile(v-if="plot", title="PCA Scree Plot", :loading="plot.loading", svg-download)
  scree-plot(
      v-if="plot.data",
      :eigenvalues="plot.data.sdev",
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
  template(v-slot:help)
    include help/ScreePlotHelp.pug
</template>
