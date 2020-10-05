<script lang="ts">
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';
import {
  computed, ComputedRef, defineComponent, reactive, toRef, watch, watchEffect,
} from '@vue/composition-api';
import ScorePlot from './ScorePlot.vue';
import LoadingsPlot from './LoadingsPlot.vue';
import usePlotData from '../use/usePlotData';
import store from '../../../store';

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  components: {
    ScorePlot,
    LoadingsPlot,
    VisTileLarge,
    LayoutGrid,
  },
  setup(props) {
    const { dataset, plot, changePlotArgs } = usePlotData(toRef(props, 'id'), 'plsda');
    const controls = reactive({
      pcXval: '1',
      pcYval: '2',
      numComponentsVal: '3',
      pcX: 1,
      pcY: 2,
      numComponents: 3,
      showEllipses: true,
      showCrosshairs: true,
      showCutoffs: true,
      showScore: true,
      showLoadings: true,
    });

    const ready = computed(() => {
      const pcaReady = store.getters.ready(props.id, 'plsda_scores');
      const loadingsReady = store.getters.ready(props.id, 'plsda_loadings');
      return pcaReady && loadingsReady;
    });
    const r2: ComputedRef<number[]> = computed(() => plot.value.data?.r2 || []);
    const q2: ComputedRef<number[]> = computed(() => plot.value.data?.q2 || []);
    const r2q2Table = computed(() => r2.value.map((r2Val, i) => ({ name: `PC${i + 1}`, r2: r2Val.toFixed(3), q2: q2.value[i].toFixed(3) })));
    const loadings = computed(() => plot.value.data?.loadings || []);
    const pcCoords = computed(() => plot.value.data?.scores.x || []);
    const eigenvalues = computed(() => plot.value.data?.scores.sdev || []);
    const rowLabels = computed(() => plot.value.data?.rows || []);
    const groupLabels = computed(() => plot.value.data?.labels || {});
    const columns = computed(() => dataset.value?.column.data || []);
    const groupLevels = computed(() => dataset.value?.groupLevels || []);

    watchEffect(() => {
      const pcX = Number.parseInt(controls.pcXval, 10);
      if (!Number.isNaN(pcX) && pcX <= controls.numComponents) {
        controls.pcX = pcX;
      }
    });
    watchEffect(() => {
      const pcY = Number.parseInt(controls.pcYval, 10);
      if (!Number.isNaN(pcY) && pcY <= controls.numComponents) {
        controls.pcY = pcY;
      }
    });
    watch(() => controls.numComponentsVal, () => {
      const numComponents = Number.parseInt(controls.numComponentsVal, 10);
      if (!Number.isNaN(numComponents)) {
        controls.numComponents = numComponents;
        if (plot.value) {
          plot.value.valid = false;
        }
        changePlotArgs({ num_of_components: controls.numComponents });
      }
    });

    return {
      plot,
      changePlotArgs,
      controls,
      ready,
      loadings,
      r2q2Table,
      pcCoords,
      eigenvalues,
      rowLabels,
      groupLabels,
      columns,
      groupLevels,
    };
  },
});
</script>

<template>
  <vis-tile-large
    title="Partial Least Squares Discriminant Analysis"
    :loading="plot.loading"
  >
    <template #controls>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
      >
        <v-toolbar-title>Components</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat
      >
        <v-card-actions>
          <v-layout column>
            <v-text-field
              v-model="controls.numComponentsVal"
              class="py-2"
              hide-details
              type="number"
              min="1"
              outline
              :disabled="plot.loading"
              label="Number of Components"
            />
          </v-layout>
        </v-card-actions>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
      >
        <v-toolbar-title>PC selector</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat
      >
        <v-card-actions>
          <v-layout column>
            <v-text-field
              v-model="controls.pcXval"
              class="py-2"
              hide-details
              type="number"
              label="PC (X Axis)"
              min="1"
              :max="controls.numComponents"
              outline
              :disabled="!controls.showScore && !controls.showLoadings"
            />
            <v-text-field
              v-model="controls.pcYval"
              class="py-2"
              hide-details
              type="number"
              label="PC (Y Axis)"
              min="1"
              :max="controls.numComponents"
              outline
              :disabled="!controls.showScore && !controls.showLoadings"
            />
          </v-layout>
        </v-card-actions>
        <v-card-text class="subheading">
          <table>
            <tbody>
              <tr>
                <th class="px-3" />
                <th class="px-3">
                  R<sup>2</sup>
                </th>
                <th class="px-3">
                  Q<sup>2</sup>
                </th>
              </tr>
              <tr
                v-for="pc in r2q2Table"
                :key="pc.name"
              >
                <td>{{ pc.name }}</td>
                <td>{{ pc.r2 }}</td>
                <td>{{ pc.q2 }}</td>
              </tr>
            </tbody>
          </table>
        </v-card-text>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
      >
        <v-toolbar-title class="switch-title">
          Score Plot
          <v-switch
            v-model="controls.showScore"
            class="switch"
            color="white"
            hide-details
          />
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat
      >
        <v-card-actions>
          <v-layout column>
            <v-switch
              v-model="controls.showEllipses"
              class="ma-0 py-2"
              label="Data ellipses"
              :disabled="!controls.showScore"
              hide-details
            />
          </v-layout>
        </v-card-actions>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
      >
        <v-toolbar-title class="switch-title">
          Loadings Plot
          <v-switch
            v-model="controls.showLoadings"
            class="switch"
            color="white"
            hide-details
          />
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mb-3 mx-3"
        flat
      >
        <v-card-actions>
          <v-layout column>
            <v-switch
              v-model="controls.showCrosshairs"
              class="ma-0 py-2"
              label="Crosshairs"
              :disabled="!controls.showLoadings"
              hide-details
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
        v-show="controls.showScore"
        :id="id"
        :pc-x="controls.pcX"
        :pc-y="controls.pcY"
        :show-ellipses="controls.showEllipses"
        :pc-coords="pcCoords"
        :row-labels="rowLabels"
        :columns="columns"
        :eigenvalues="eigenvalues"
        :group-labels="groupLabels"
        :group-levels="groupLevels"
      />
      <loadings-plot
        v-show="controls.showLoadings"
        :id="id"
        :pc-x="controls.pcX"
        :pc-y="controls.pcY"
        :show-crosshairs="controls.showCrosshairs"
        :loadings="loadings"
      />
    </layout-grid>
    <div v-else>
      <v-progress-circular
        indeterminate
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
