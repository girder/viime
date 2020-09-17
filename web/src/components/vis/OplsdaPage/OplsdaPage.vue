<script lang="ts">
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';
import {
  computed, defineComponent, reactive, toRef, toRefs, watchEffect,
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
    const { dataset, plot, changePlotArgs } = usePlotData(toRef(props, 'id'), 'oplsda');
    const controls = reactive({
      pcYval: '1',
      pcY: 2,
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
    const r2 = computed(() => plot.value.data?.r2 || []);
    const loadings = computed(() => plot.value.data?.loadings || []);
    const pcCoords = computed(() => plot.value.data?.scores.x || []);
    const eigenvalues = computed(() => plot.value.data?.scores.sdev || []);
    const rowLabels = computed(() => plot.value.data?.rows || []);
    const groupLabels = computed(() => plot.value.data?.labels || {});
    const columns = computed(() => dataset.value?.column.data || []);
    const groupLevels = computed(() => dataset.value?.groupLevels || []);

    watchEffect(() => {
      const pcY = Number.parseInt(controls.pcYval, 10);
      if (!Number.isNaN(pcY)) {
        // The first of the 6 components is always pcX
        // We want to express pcY as an integer in [1..5], but use it as a number in [2..6]
        controls.pcY = pcY + 1;
      }
    });

    return {
      plot,
      changePlotArgs,
      ...toRefs(controls),
      ready,
      r2,
      loadings,
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
        dark="dark"
        flat="flat"
        dense="dense"
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
              v-model="pcYval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="O (Y Axis)"
              min="1"
              max="5"
              outline="outline"
              :disabled="!showScore &amp;&amp; !showLoadings"
            />
          </v-layout>
        </v-card-actions>
        <v-card-text class="subheading">
          <div
            v-for="(r2Val,index) in r2"
            :key="index"
            :class="(index===pcY-1)? 'font-weight-bold':''"
            @click="if (index !== 0) pcYval=index"
          >
            <template v-if="index === 0">
              P
            </template>
            <template v-else>
              O{{ index }}
            </template>
            R<sup>2</sup>: {{ r2Val }}
          </div>
        </v-card-text>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
      >
        <v-toolbar-title class="switch-title">
          Score Plot
          <v-switch
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
      >
        <v-toolbar-title class="switch-title">
          Loadings Plot
          <v-switch
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
    </template>
    <layout-grid
      v-if="ready"
      :cell-size="300"
    >
      <score-plot
        v-show="showScore"
        :id="id"
        :pc-x="1"
        :pc-y="pcY"
        :show-ellipses="showEllipses"
        :pc-coords="pcCoords"
        :row-labels="rowLabels"
        :columns="columns"
        :eigenvalues="eigenvalues"
        :group-labels="groupLabels"
        :group-levels="groupLevels"
      />
      <loadings-plot
        v-show="showLoadings"
        :id="id"
        :pc-x="1"
        :pc-y="pcY"
        :show-crosshairs="showCrosshairs"
        :loadings="loadings"
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
