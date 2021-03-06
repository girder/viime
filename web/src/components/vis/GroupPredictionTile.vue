<script lang="ts">
import {
  defineComponent, computed, ref, toRef, watch, Ref, reactive,
} from '@vue/composition-api';
import RocCurve from './RocCurve.vue';
import VisTileLarge from './VisTileLarge.vue';
import { CSVService } from '../../common/api.service';
import usePlotData from './use/usePlotData';

interface Column {
  column_type: string;
  column_header: string;
}
interface Level {
  name: string;
}
interface PCAData {
  factor: number[];
  metabolites: string[];
}

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  components: {
    VisTileLarge,
    RocCurve,
  },

  setup(props) {
    const controls = reactive({
      metabolites: [] as string[], // currently selected metabolites
      threshold: 0.4, // threshold for factor analysis
      maxThreshold: 1,
      group1: '',
      group2: '',
      metaboliteSource: null as number | null,
      analysis: 'all',
      analysisOptions: [
        { value: 'all', text: 'All metabolites' },
        { value: 'selected', text: 'Selected Metabolites' },
        { value: 'factor', text: 'Factor Analysis' },
        { value: 'plsda', text: 'PLSDA' },
        { value: 'oplsda', text: 'OPLSDA' },
      ],
      method: 'random_forest',
      methodOptions: [
        { value: 'random_forest', text: 'Random Forest' },
        { value: 'logistic_regression', text: 'Logistic Regression' },
      ],
      displayConfidenceInterval: false,
    });

    const pcaData: Ref<PCAData | null> = ref(null);// data from factor analysis endpoint

    const { plot, dataset, changePlotArgs } = usePlotData(toRef(props, 'id'), 'roc');

    // Column names (i.e. metabolites) available for selection,
    // filtered based on current metabolite source
    const columns = computed(() => {
      if (controls.analysis === 'all') {
        return dataset.value.column.data.filter((column: Column) => column.column_type === 'measurement')
          .map((column: Column) => column.column_header);
      }
      if (controls.analysis === 'selected') {
        return dataset.value.selectedColumns;
      }
      if (!pcaData.value?.metabolites) {
        return [];
      }
      const pcaDataValue = pcaData.value;
      if (!pcaDataValue?.metabolites) {
        return [];
      }
      const { metabolites } = pcaDataValue;
      return metabolites.filter((m, i) => (pcaDataValue.factor[i] === controls.metaboliteSource));
    });
    const groups = computed(() => dataset.value.groupLevels.map((level: Level) => level.name));
    const metaboliteSourceOptions = computed(() => {
      const options = pcaData.value?.factor.map((factor) => ({ value: factor, text: `PC${factor}` }));
      if (!options) {
        return [];
      }
      return options;
    });
    // The "All" and "Selected" analysis options do not do any analysis,
    // so we don't want to show the Metabolite Source selector
    const showMetaboliteSource = computed(() => controls.analysis !== 'all' && controls.analysis !== 'selected' && controls.analysis !== 'oplsda');
    const sensitivities = computed(() => {
      if (!plot.value.data
        || !controls.group1
        || !controls.group2
        || controls.metabolites.length === 0) {
        return [];
      }
      return plot.value.data.sensitivities;
    });
    const specificities = computed(() => {
      if (!plot.value.data
        || !controls.group1
        || !controls.group2
        || controls.metabolites.length === 0) {
        return [];
      }
      return plot.value.data.specificities;
    });
    const auc = computed(() => {
      if (!plot.value.data
        || !controls.group1
        || !controls.group2
        || controls.metabolites.length === 0) {
        return 0;
      }
      return plot.value.data.auc[0];
    });
    const lowerBound = computed(() => {
      if (!plot.value.data
        || !controls.group1
        || !controls.group2
        || controls.metabolites.length === 0) {
        return [];
      }
      return plot.value.data.lower_bound;
    });
    const upperBound = computed(() => {
      if (!plot.value.data
        || !controls.group1
        || !controls.group2
        || controls.metabolites.length === 0) {
        return [];
      }
      return plot.value.data.upper_bound;
    });

    // Called when a metabolite is removed from the ROC analysis
    // as a result of the user clicking the red 'X' next to its
    // name in the 'Metabolites' autoselect
    function removeMetabolite(metabolite: string) {
      controls.metabolites.splice(controls.metabolites.indexOf(metabolite), 1);
      changePlotArgs({ columns: JSON.stringify(controls.metabolites) });
    }
    async function getFactors() {
      try {
        // perform factor analysis
        if (controls.analysis === 'factor') {
          const pcaDataResponse = await CSVService.getAnalysis(dataset.value.id, 'factors', { threshold: controls.threshold });
          pcaData.value = pcaDataResponse?.data?.metabolites ? pcaDataResponse.data : null;
        } else if (controls.analysis === 'plsda') {
          // TODO add controls for num_of_components?
          const plsdaDataResponse = await CSVService.getAnalysis(dataset.value.id, 'plsda_factors',
            {
              num_of_components: 4,
              threshold: controls.threshold,
            });
          pcaData.value = plsdaDataResponse.data;
          controls.maxThreshold = plsdaDataResponse.data.max_vip;
        } else if (controls.analysis === 'oplsda') {
          // TODO add controls for num_of_components?
          const oplsdaDataResponse = await CSVService.getAnalysis(dataset.value.id, 'oplsda_factors',
            {
              num_of_components: 2,
              threshold: controls.threshold,
              group1: controls.group1,
              group2: controls.group2,
            });
          pcaData.value = oplsdaDataResponse.data;
          controls.maxThreshold = oplsdaDataResponse.data.max_vip;
          controls.metaboliteSource = 0;
        }
        // update the selected metabolites to the result of the analysis
        controls.metabolites = columns.value;
      } catch (err) {
        pcaData.value = null;
      }
    }

    // Perform an initial factor analysis
    getFactors();

    // get new factor analysis when threshold changes
    watch(() => controls.threshold, () => {
      getFactors();
    });

    // Clear metabolites when analysis is changed to 'All'
    // If the source is changed to 'Selected' or one of the PC factors,
    // populate the list with the filtered metabolite and graph them.
    watch(() => controls.analysis, (newAnalysis) => {
      controls.metaboliteSource = null;
      controls.metabolites = newAnalysis === 'all' ? [] : columns.value;
      changePlotArgs({ columns: JSON.stringify(controls.metabolites) });
      getFactors();
    });
    watch(() => controls.metaboliteSource, () => {
      controls.metabolites = columns.value;
      changePlotArgs({ columns: JSON.stringify(controls.metabolites) });
    });
    watch(() => controls.metabolites, () => {
      changePlotArgs({ columns: JSON.stringify(controls.metabolites) });
    });
    // These two watchers prevent the same group from being selected twice.
    // And also rerun the analysis if the analysis is OPLSDA,
    // since OPLSDA takes the groups as arguments.
    watch(() => controls.group1, (newGroup, oldGroup) => {
      changePlotArgs({ group1: newGroup });
      if (controls.group2 === newGroup) {
        controls.group2 = oldGroup;
        changePlotArgs({ group2: oldGroup });
      }
      if (controls.analysis === 'oplsda') {
        getFactors();
      }
    });
    watch(() => controls.group2, (newGroup, oldGroup) => {
      changePlotArgs({ group2: newGroup });
      if (controls.group1 === newGroup) {
        controls.group1 = oldGroup;
        changePlotArgs({ group1: oldGroup });
      }
      if (controls.analysis === 'oplsda') {
        getFactors();
      }
    });
    return {
      controls,
      pcaData,
      plot,
      changePlotArgs,
      columns,
      groups,
      showMetaboliteSource,
      metaboliteSourceOptions,
      sensitivities,
      specificities,
      auc,
      lowerBound,
      upperBound,
      removeMetabolite,
    };
  },
});
</script>

<template>
  <vis-tile-large
    v-if="plot"
    title="Group Prediction"
    analysis-path="roc"
    :loading="plot.loading"
    expanded
    download
  >
    <template #controls>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>Analysis</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat
      >
        <v-select
          v-model="controls.analysis"
          class="py-2"
          hide-details
          :items="controls.analysisOptions"
        />
      </v-card>
      <v-toolbar
        v-if="showMetaboliteSource"
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>Metabolite Source</v-toolbar-title>
      </v-toolbar>
      <v-card
        v-if="showMetaboliteSource"
        class="mx-3 px-2"
        flat
      >
        <v-select
          v-model="controls.metaboliteSource"
          class="py-2"
          hide-details
          :items="metaboliteSourceOptions"
        />
      </v-card>
      <v-toolbar
        v-if="showMetaboliteSource"
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>
          Loading Threshold
          <v-tooltip
            v-if="!pcaData"
            slot="append"
            right
          >
            <v-icon
              slot="activator"
              color="error"
            >
              {{ $vuetify.icons.warningCircle }}
            </v-icon>
            <span>
              Factor analysis with loading threshold of <br>
              {{ controls.threshold }} returned 0 metabolites.
            </span>
          </v-tooltip>
        </v-toolbar-title>
      </v-toolbar>
      <v-card
        v-if="showMetaboliteSource"
        class="mx-3"
        flat
      >
        <v-card-actions>
          <v-layout column>
            <v-slider
              class="my-1 minCorrelation"
              :value="controls.threshold"
              label="0"
              thumb-label="always"
              hide-details
              min="0"
              :max="controls.maxThreshold"
              step="0.1"
              style="padding-top: 16px;"
              @change="controls.threshold = $event"
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
        :card="false"
      >
        <v-toolbar-title v-text="`Metabolites (${controls.metabolites.length})`" />
      </v-toolbar>
      <v-card
        class="mx-3 px-1"
        flat
      >
        <v-autocomplete
          v-model="controls.metabolites"
          :items="columns"
          chips
          dense
          multiple
          clearable
          deletable-chips
          auto-select-first
          hide-selected
          hide-details
        >
          <template v-slot:selection="data">
            <v-tooltip right>
              <template v-slot:activator="{ on }">
                <v-chip
                  small
                  v-on="on"
                >
                  <v-icon
                    class="closePillButton pr-1"
                    small
                    @click.stop="removeMetabolite(data.item)"
                  >
                    mdi-close
                  </v-icon><span class="searchResult">{{ data.item }}</span>
                </v-chip>
              </template><span>{{ data.item }}</span>
            </v-tooltip>
          </template>
        </v-autocomplete>
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>Group 1</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat
      >
        <v-select
          v-model="controls.group1"
          class="py-2"
          hide-details
          :items="groups"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>Group 2</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat
      >
        <v-select
          v-model="controls.group2"
          class="py-2"
          hide-details
          :items="groups"
        />
      </v-card>
      <v-toolbar
        class="darken-3"
        color="primary"
        dark
        flat
        dense
        :card="false"
      >
        <v-toolbar-title>Method</v-toolbar-title>
      </v-toolbar>
      <v-card
        class="mx-3 px-2"
        flat
      >
        <v-select
          v-model="controls.method"
          class="py-2"
          hide-details
          :items="controls.methodOptions"
          @change="changePlotArgs({method: $event})"
        />
        <v-card-actions>
          <v-layout column>
            <v-switch
              v-model="controls.displayConfidenceInterval"
              class="ma-0 py-2"
              label="Confidence Interval"
              hide-details
            />
          </v-layout>
        </v-card-actions>
      </v-card>
    </template>
    <roc-curve
      :specificities="specificities"
      :sensitivities="sensitivities"
      :auc="auc"
      :display-confidence-interval="controls.displayConfidenceInterval"
      :lower-bound="lowerBound"
      :upper-bound="upperBound"
    />
  </vis-tile-large>
</template>

<style>
.closePillButton:hover {
  color: red;
}

.searchResult {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  width: 100px;
}
</style>
