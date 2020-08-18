<script>
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import LayoutGrid from '@/components/LayoutGrid.vue';
import ScorePlot from './ScorePlot.vue';
import LoadingsPlot from './LoadingsPlot.vue';
import plotData from '../mixins/plotData';

export default {
  components: {
    ScorePlot,
    LoadingsPlot,
    VisTileLarge,
    LayoutGrid,
  },

  mixins: [plotData('plsda')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      pcXval: '1',
      pcYval: '2',
      numComponentsVal: '10',
      pcX: 1,
      pcY: 2,
      numComponents: 10,
      showEllipses: true,
      showCrosshairs: true,
      showCutoffs: true,
      showScore: true,
      showLoadings: true,
    };
  },

  computed: {
    ready() {
      const pcaReady = this.$store.getters.ready(this.id, 'plsda_scores');
      const loadingsReady = this.$store.getters.ready(this.id, 'plsda_loadings');
      return pcaReady && loadingsReady;
    },
    loadings() {
      return this.maybeData(['loadings'], []);
    },
    pcCoords() {
      return this.maybeData(['scores', 'x'], []);
    },
    eigenvalues() {
      return this.maybeData(['scores', 'sdev'], []);
    },
    rowLabels() {
      return this.maybeData(['rows'], []);
    },
    groupLabels() {
      return this.maybeData(['labels'], []);
    },
    columns() {
      if (this.dataset?.column?.data) {
        return this.dataset.column.data;
      }
      return [];
    },

    groupLevels() {
      if (this.dataset?.groupLevels) {
        return this.dataset.groupLevels;
      }
      return [];
    },
  },
  watch: {
    pcXval: {
      handler(val) {
        const pcX = Number.parseInt(val, 10);
        if (!Number.isNaN(pcX)) {
          this.pcX = pcX;
        }
      },
      immediate: true,
    },
    pcYval: {
      handler(val) {
        const pcY = Number.parseInt(val, 10);
        if (!Number.isNaN(pcY)) {
          this.pcY = pcY;
        }
      },
      immediate: true,
    },
    numComponentsVal: {
      handler(val) {
        const numComponents = Number.parseInt(val, 10);
        if (!Number.isNaN(numComponents)) {
          this.numComponents = numComponents;
        }
      },
      immediate: true,
    },
  },
  methods: {
    maybeData(keys, dflt) {
      const {
        plot,
      } = this;
      if (keys.length === 2) {
        return plot.data ? plot.data[keys[0]][keys[1]] : dflt;
      }
      return plot.data ? plot.data[keys[0]] : dflt;
    },
  },
};
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
        <v-toolbar-title>Components</v-toolbar-title>
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
              hide-details="hide-details"
              type="number"
              min="1"
              outline="outline"
              :disabled="plot.loading"
              label="Number of Components"
              @change="changePlotArgs({ num_of_components: $event });"
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
              :disabled="!showScore &amp;&amp; !showLoadings"
            />
            <v-text-field
              v-model="pcYval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="PC (Y Axis)"
              min="1"
              outline="outline"
              :disabled="!showScore &amp;&amp; !showLoadings"
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
        :pc-x="pcX"
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
        :pc-x="pcX"
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
