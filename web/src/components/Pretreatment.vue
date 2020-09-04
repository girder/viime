<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api';
import store from '../store';
import { LOAD_DATASET } from '../store/actions.type';
import { INTIALIZE_DATASET, SET_SELECTION } from '../store/mutations.type';
import router from '../router';
import analyses from './vis/analyses';

interface Dataset {
  id: string;
}

interface Problem {
  multi: boolean;
  type: string;
  context: string;
  row_index?: string;
  column_index?: string;
}

export default defineComponent({
  props: {
    problem: {
      type: String,
      default: null,
    },
    id: {
      type: String,
      required: true,
      default: null,
    },
  },
  setup(props) {
    const datasets = ref(store.state.datasets);

    function valid(dataset: Dataset) {
      return store.getters.valid(dataset.id);
    }
    function isMerged(dataset: Dataset) {
      return store.getters.isMerged(dataset.id);
    }
    function problemNav(problem: Problem, id: string) {
      if (problem.multi) {
        router.push({ name: 'Problem', params: { id, problem: problem.type } }).catch(() => { });
      } else {
        router.push({ name: 'Clean Up Table', params: { id } }).catch(() => { });
        store.commit(SET_SELECTION, {
          key: id,
          event: {},
          axis: problem.context,
          // eslint-disable-next-line no-nested-ternary
          idx: (problem.context === 'row') ? problem.row_index
            : (problem.context === 'column') ? problem.column_index
              : undefined,
        });
      }
    }

    const dataset = store.getters.dataset(props.id);
    if (!dataset.value) {
      // initialize the dataset to prevent NPE race conditions during slow loads
      store.commit(INTIALIZE_DATASET, { dataset_id: props.id });
      store.dispatch(LOAD_DATASET, { dataset_id: props.id });
    }
    return {
      datasets,
      analyses,
      valid,
      isMerged,
      problemNav,
    };
  },
});
</script>

<template>
  <v-layout
    class="pretreatment-component"
    row="row"
    fill-height="fill-height"
  >
    <v-navigation-drawer
      class="navigation"
      floating="floating"
      permanent="permanent"
      style="min-width: 220px; width: 220px;"
      touchless="touchless"
      disable-resize-watcher="disable-resize-watcher"
      stateless="stateless"
    >
      <v-list
        class="py-0"
        dense="dense"
      >
        <v-list-group
          v-for="(dataset) in datasets"
          :key="dataset.id"
          :class="{ active: $route.name === 'Pretreat Data' && dataset.id === id }"
          :value="dataset.id === id"
        >
          <template #activator>
            <v-list-tile
              class="mr-0 pr-2"
              active-class="font-weight-bold"
              :to="{ name: 'Pretreat Data', params: { id: dataset.id } }"
              exact="exact"
              @click.stop=""
            >
              <v-list-tile-title class="grow">
                {{ dataset.name }}
              </v-list-tile-title>
              <v-list-tile-action class="action-style">
                <v-icon
                  v-if="dataset.validation.length"
                  color="warning"
                >
                  {{ $vuetify.icons.warning }}
                </v-icon>
                <v-icon
                  v-else
                  color="success"
                >
                  {{ $vuetify.icons.check }}
                </v-icon>
              </v-list-tile-action>
            </v-list-tile>
          </template>
          <v-list-tile
            :to="{ name: 'Clean Up Table', params: { id: dataset.id } }"
            exact="exact"
            active-class="font-weight-bold"
          >
            <v-list-tile-action class="action-style">
              <v-icon>{{ $vuetify.icons.tableEdit }}</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Clean Up Table</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile
            v-for="problemData in dataset.validation"
            :key="problemData.title"
            :class="{ active: problemData.type === problem && dataset.id === id }"
            :inactive="!problemData.clickable"
            active-class="font-weight-bold"
            @click="problemNav(problemData, dataset.id)"
          >
            <v-list-tile-action class="action-style">
              <v-icon
                class="pr-1"
                :color="problemData.severity"
              >
                {{ $vuetify.icons[problemData.severity] }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                {{ problemData.title }}
                <span v-if="problemData.data">({{ problemData.data.length }})</span>
                <v-tooltip
                  v-else
                  top="top"
                >
                  <template #activator="{ on }">
                    <v-icon
                      class="pr-1"
                      small="small"
                      v-on="on"
                    >
                      {{ $vuetify.icons.info }}
                    </v-icon>
                  </template><span>{{ problemData.description }}</span>
                </v-tooltip>
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile
            v-show="!isMerged(dataset)"
            :to="{ name: 'Impute Table', params: { id: dataset.id } }"
            active-class="font-weight-bold"
          >
            <v-list-tile-action class="action-style">
              <v-icon class="pr-1">
                {{ $vuetify.icons.tableEdit }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Impute Table</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list-tile
            v-show="!isMerged(dataset)"
            :to="{ name: 'Transform Table', params: { id: dataset.id } }"
            :disabled="!valid(dataset)"
            active-class="font-weight-bold"
          >
            <v-list-tile-action class="action-style">
              <v-icon class="pr-1">
                {{ $vuetify.icons.bubbles }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Transform Table</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
          <v-list class="py-0">
            <v-list-group :class="{ active: $route.name === 'Analyze Data' && dataset.id === id }">
              <template #activator>
                <v-list-tile
                  :to="{ name: 'Analyze Data', params: { id: dataset.id } }"
                  :disabled="!valid(dataset)"
                  exact="exact"
                  active-class="font-weight-bold"
                >
                  <v-list-tile-action class="action-style">
                    <v-icon class="pr-1">
                      {{ $vuetify.icons.cogs }}
                    </v-icon>
                  </v-list-tile-action>
                  <v-list-tile-content>
                    <v-list-tile-title>Analyze Table</v-list-tile-title>
                  </v-list-tile-content>
                </v-list-tile>
              </template>
              <v-list-tile
                v-for="a in analyses"
                :key="a.path"
                :to="{ name: a.shortName, params: { id: dataset.id } }"
                :disabled="!valid(dataset)"
                active-class="font-weight-bold"
              >
                <v-list-tile-action class="action-style">
                  <v-icon
                    class="pr-1"
                    :style="a.iconStyle"
                  >
                    {{ a.icon || $vuetify.icons.compare }}
                  </v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                  <v-list-tile-title>{{ a.shortName }}</v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
            </v-list-group>
          </v-list>
          <v-list-tile
            :to="{ name: 'Download Data', params: { id: dataset.id } }"
            :disabled="!valid(dataset)"
            active-class="font-weight-bold"
          >
            <v-list-tile-action class="action-style">
              <v-icon class="pr-1">
                {{ $vuetify.icons.fileDownload }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>Download Data</v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
    <router-view />
  </v-layout>
</template>

<style scoped>
.action-style {
  min-width: 40px !important;
}
</style>
