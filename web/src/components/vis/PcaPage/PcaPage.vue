<script lang="ts">
import {
  defineComponent, computed, reactive, toRefs, watch,
} from '@vue/composition-api';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';
import store from '../../../store';
import ScorePlot from './ScorePlot.vue';
import ScreePlot from './ScreePlot.vue';
import LoadingsPlot from './LoadingsPlot.vue';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  components: {
    ScorePlot,
    ScreePlot,
    LoadingsPlot,
    VisTileLarge,
    LayoutGrid,
  },
  setup(props) {
    const plot = reactive({
      pcXval: '1',
      pcYval: '2',
      numComponentsVal: '10',
      pcX: 1,
      pcY: 2,
      numComponents: 10,
      showEllipses: true,
      showCrosshairs: true,
      showCutoffs: true,
      showScree: true,
      showScore: true,
      showLoadings: true,
    });

    const ready = computed(() => {
      const pcaReady = store.getters.ready(props.id, 'pca');
      const loadingsReady = store.getters.ready(props.id, 'loadings');

      return pcaReady && loadingsReady;
    });

    watch(() => plot.pcXval, (newPcXval) => {
      const newPcX = Number.parseInt(newPcXval, 10);
      if (!Number.isNaN(newPcX)) {
        plot.pcX = newPcX;
      }
    });
    watch(() => plot.pcYval, (newPcYval) => {
      const newPcY = Number.parseInt(newPcYval, 10);
      if (!Number.isNaN(newPcY)) {
        plot.pcY = newPcY;
      }
    });
    watch(() => plot.numComponentsVal, (newNumComponentsVal) => {
      const newNumComponents = Number.parseInt(newNumComponentsVal, 10);
      if (!Number.isNaN(newNumComponents)) {
        plot.numComponents = newNumComponents;
      }
    });

    return {
      ...toRefs(plot),
      ready,
    };
  },
});
</script>
<template>
  <vis-tile-large
    title="Principal Component Analysis"
    :loading="false"
  >
    <template #controls>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title>PC selector</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat="flat"
      >
        <v-card-actions>
          <v-layout column="column">
            <v-text-field
              v-model="pcXval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="PC (X Axis)"
              min="1"
              outline="outline"
              :disabled="!showScore && !showLoadings"
            />
            <v-text-field
              v-model="pcYval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="PC (Y Axis)"
              min="1"
              outline="outline"
              :disabled="!showScore && !showLoadings"
            />
          </v-layout>
        </v-card-actions>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title class="switch-title">
          Score Plot<v-switch
            v-model="showScore"
            class="switch"
            color="white"
            hide-details="hide-details"
          />
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat="flat"
      >
        <v-card-actions>
          <v-layout column="column">
            <v-switch
              v-model="showEllipses"
              class="ma-0 py-2"
              label="Data ellipses"
              :disabled="!showScore"
              hide-details="hide-details"
            />
          </v-layout>
        </v-card-actions>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title class="switch-title">
          Loadings Plot<v-switch
            v-model="showLoadings"
            class="switch"
            color="white"
            hide-details="hide-details"
          />
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat="flat"
      >
        <v-card-actions>
          <v-layout column="column">
            <v-switch
              v-model="showCrosshairs"
              class="ma-0 py-2"
              label="Crosshairs"
              :disabled="!showLoadings"
              hide-details="hide-details"
            />
          </v-layout>
        </v-card-actions>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title class="switch-title">
          Scree Plot<v-switch
            v-model="showScree"
            class="switch"
            color="white"
            hide-details="hide-details"
          />
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat="flat"
      >
        <v-card-actions>
          <v-layout column="column">
            <v-text-field
              v-model="numComponentsVal"
              class="py-2"
              :disabled="!showScree"
              hide-details="hide-details"
              type="number"
              label="Number of PCs"
              min="1"
              outline="outline"
            />
            <v-switch
              v-model="showCutoffs"
              class="ma-0 py-2"
              label="Cutoff lines"
              :disabled="!showScree"
              hide-details="hide-details"
            />
          </v-layout>
        </v-card-actions>
      </v-card>
    </template>
    <layout-grid
      v-if="ready"
      :cell-size="300"
    >
      <score-plot
        v-show="showScore"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :show-ellipses="showEllipses"
      />
      <loadings-plot
        v-show="showLoadings"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :show-crosshairs="showCrosshairs"
      />
      <scree-plot
        v-show="showScree"
        :id="id"
        :pc-x="pcX"
        :pc-y="pcY"
        :num-components="numComponents"
        :show-cutoffs="showCutoffs"
      />
    </layout-grid>
    <div v-else>
      <v-progress-circular
        indeterminate="indeterminate"
        size="100"
        width="5"
      />
      <h4 class="display-1 pa-3">
        Loading data...
      </h4>
    </div>
  </vis-tile-large>
</template>

<style lang="scss" scoped>
.switch-title {
  align-items: center;
  display: flex;
  justify-content: space-between;
  overflow: visible;
  width: 100%;
  .switch {
    flex-grow: 0;
    margin-right: -10px;
  }
}
</style>
