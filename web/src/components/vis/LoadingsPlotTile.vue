<script>
import LoadingsPlot from './LoadingsPlot.vue';
import LoadingsPlotHelp from './help/LoadingsPlotHelp.vue';
import VisTile from './VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    LoadingsPlot,
    LoadingsPlotHelp,
    VisTile,
  },

  mixins: [plotData('loadings')],

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
      showCrosshairs: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval, 10);
    },

    pcY() {
      return Number.parseInt(this.pcYval, 10);
    },
  },
};

</script>

<template>
  <vis-tile
    v-if="plot"
    title="PCA Loadings Plot"
    :loading="plot.loading"
    svg-download="svg-download"
  >
    <loadings-plot
      :points="plot.data"
      :pc-x="pcX"
      :pc-y="pcY"
      :show-crosshairs="showCrosshairs"
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
          <v-layout column="column">
            <v-text-field
              v-model="pcXval"
              class="pa-2"
              hide-details="hide-details"
              type="number"
              label="PC (X Axis)"
              min="1"
              outline="outline"
            />
            <v-text-field
              v-model="pcYval"
              class="pa-2"
              hide-details="hide-details"
              type="number"
              label="PC (Y Axis)"
              min="1"
              outline="outline"
            />
            <v-switch
              v-model="showCrosshairs"
              class="ma-2"
              hide-details="hide-details"
              label="Show crosshairs"
            />
          </v-layout>
        </v-card>
      </v-menu>
    </template>
    <template v-slot:help>
      <LoadingsPlotHelp />
    </template>
  </vis-tile>
</template>
