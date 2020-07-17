<script>
import RocCurve from './RocCurve.vue';
import VisTileLarge from './VisTileLarge.vue';
import { CSVService } from '../../common/api.service';
import plotData from './mixins/plotData';

export default {
  components: {
    VisTileLarge,
    RocCurve,
  },

  mixins: [plotData('roc')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      metabolites: [],
      group1: '',
      group2: '',
      metaboliteSource: 'all',
      metaboliteSourceOptions: [
        { value: 'all', text: 'All metabolites' },
        { value: 'selected', text: 'Selected Metabolites' },
      ],
      method: 'random_forest',
      methodOptions: [
        { value: 'random_forest', text: 'Random Forest' },
        { value: 'logistic_regression', text: 'Logistic Regression' },
      ],
      pcaData: null,
    };
  },
  computed: {
    columns() {
      if (this.metaboliteSource === 'all') {
        return this.dataset.column.data.filter((column) => column.column_type === 'measurement')
          .map((column) => column.column_header);
      } 
      if (this.metaboliteSource === 'selected') {
        return this.dataset.selectedColumns;
      }
      return this.pcaData.metabolites.filter((metabolite, index) => this.pcaData.factor[index] === this.metaboliteSource);
    },
    groups() {
      return this.dataset.groupLevels.map((level) => level.name);
    },
    rocData() {
      if (!this.plot.data) {
        return { sensitivities: [], specificities: [], auc: 0 };
      }
      return {
        sensitivities: this.plot.data.sensitivities,
        specificities: this.plot.data.specificities,
        auc: this.plot.data.auc[0],
      };
    },
  },
  async mounted() {
    const pcaDataResponse = await CSVService.getAnalysis(this.dataset.id, 'factors', {});
    this.pcaData = pcaDataResponse.data;
    this.pcaData.factor.forEach((factor) => {
      this.metaboliteSourceOptions.push({
        value: factor,
        text: `PC${factor}`,
      });
    });
  },
};
</script>

<template>
  <vis-tile-large
    v-if="plot"
    title="Group Prediction"
    :loading="plot.loading"
    expanded="expanded"
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
        <v-toolbar-title>Metabolite Source</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat="flat"
      >
        <v-select
          v-model="metaboliteSource"
          class="py-2"
          hide-details="hide-details"
          :items="metaboliteSourceOptions"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title>Metabolite</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat="flat"
      >
        <v-autocomplete
          v-model="metabolites"
          :items="columns"
          chips="chips"
          dense="dense"
          multiple
          deletable-chips="deletable-chips"
          auto-select-first="auto-select-first"
          hide-selected="hide-selected"
          hide-details="hide-details"
          @change="changePlotArgs({columns: JSON.stringify(metabolites)})"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title>Group 1</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat="flat"
      >
        <v-select
          v-model="group1"
          class="py-2"
          hide-details="hide-details"
          :items="groups"
          @change="changePlotArgs({group1: $event})"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title>Group 2</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat="flat"
      >
        <v-select
          v-model="group2"
          class="py-2"
          hide-details="hide-details"
          :items="groups"
          @change="changePlotArgs({group2: $event})"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark="dark"
        flat="flat"
        dense="dense"
        :card="false"
      >
        <v-toolbar-title>Method</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat="flat"
      >
        <v-select
          v-model="method"
          class="py-2"
          hide-details="hide-details"
          :items="methodOptions"
          @change="changePlotArgs({method: $event})"
        />
      </v-card>
    </template>
    <roc-curve :roc-data="rocData" />
  </vis-tile-large>
</template>

<style>
.horizontalScrollable {
  position: absolute;
}

.minCorrelation {
  padding-top: 16px;
}

.minCorrelation >>> .v-input__slot::after {
  content: "0.1";
  color: rgba(0,0,0,0.54);
  margin-left: 16px;
}
</style>
