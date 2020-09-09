<script lang="ts">
import {
  defineComponent, computed, ref, toRef,
} from '@vue/composition-api';
import ScreePlot from '@/components/vis/ScreePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import ScreePlotHelp from './help/ScreePlotHelp.vue';
import usePlotData from './use/usePlotData';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },

  components: {
    ScreePlot,
    ScreePlotHelp,
    VisTile,
  },

  setup(props) {
    const showCutoffs = ref(true);
    const numComponentsText = ref('10');
    const numComponents = computed(() => Number.parseInt(numComponentsText.value, 10));

    const { plot } = usePlotData(toRef(props, 'id'), 'pca');

    return {
      numComponentsText,
      numComponents,
      showCutoffs,
      plot,
    };
  },
});
</script>

<template>
  <vis-tile
    v-if="plot"
    title="PCA Scree Plot"
    :loading="plot.loading"
    svg-download="svg-download"
  >
    <scree-plot
      v-if="plot.data"
      :eigenvalues="plot.data.sdev"
      :num-components="numComponents"
      :show-cutoffs="showCutoffs"
    /><template v-slot:controls>
      <v-menu
        bottom="bottom"
        offset-y="offset-y"
        left="left"
        :min-width="150"
        :close-on-content-click="false"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            icon="icon"
            v-on="on"
          >
            <v-icon class="mdi mdi-dots-vertical" />
          </v-btn>
        </template>
        <v-card
          class="pa-1"
          flat="flat"
        >
          <v-layout
            class="px-2"
            column="column"
          >
            <v-text-field
              v-model="numComponentsText"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="Principal Components"
              min="1"
              outline="outline"
            />
            <v-switch
              v-model="showCutoffs"
              class="py-2"
              label="Diagnostic cutoffs"
              hide-details="hide-details"
            />
          </v-layout>
        </v-card>
      </v-menu>
    </template>
    <template v-slot:help>
      <ScreePlotHelp />
    </template>
  </vis-tile>
</template>
