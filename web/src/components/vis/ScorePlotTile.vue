<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import ScorePlotHelp from './help/ScorePlotHelp.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ScorePlot,
    ScorePlotHelp,
    VisTile,
  },

  mixins: [plotData('pca')],

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
      showEllipses: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval, 10);
    },

    pcY() {
      return Number.parseInt(this.pcYval, 10);
    },

    pcCoords() {
      return this.maybeData('x', []);
    },

    rowLabels() {
      return this.maybeData('rows', []);
    },

    groupLabels() {
      return this.maybeData('labels', {});
    },

    eigenvalues() {
      return this.maybeData('sdev', []);
    },

    columns() {
      return this.dataset.column.data;
    },
  },

  methods: {
    maybeData(key, dflt) {
      const {
        plot,
      } = this;

      return plot.data ? plot.data[key] : dflt;
    },
  },
};

</script>

<template>
  <vis-tile
    title="PCA Score Plot"
    svg-download="svg-download"
  >
    <score-plot
      :pc-coords="pcCoords"
      :row-labels="rowLabels"
      :colors="dataset.groupLevels"
      :group-labels="groupLabels"
      :eigenvalues="eigenvalues"
      :columns="columns"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-ellipses="showEllipses"
    />
    <template v-slot:controls>
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
              v-model="pcXval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="PC (X Axis)"
              min="1"
              outline="outline"
            />
            <v-text-field
              v-model="pcYval"
              class="py-2"
              hide-details="hide-details"
              type="number"
              label="PC (Y Axis)"
              min="1"
              outline="outline"
            />
            <v-switch
              v-model="showEllipses"
              class="py-2"
              label="Data ellipses"
              hide-details="hide-details"
            />
          </v-layout>
        </v-card>
      </v-menu>
    </template>
    <template v-slot:help>
      <ScorePlotHelp />
    </template>
  </vis-tile>
</template>
