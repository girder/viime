<script lang="ts">
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import {
  defineComponent, ref, computed, watch, Ref,
} from '@vue/composition-api';
import store from '../store';
import {
  LOAD_DATASET,
  SET_DATASET_NAME, SET_DATASET_DESCRIPTION, SET_DATASET_GROUP_LEVELS, REMERGE_DATASET,
} from '../store/actions.type';
import { INTIALIZE_DATASET } from '../store/mutations.type';

import MergeMethods from './MergeMethods.vue';

interface Dataset {
  id: string;
  created: Date;
  name: string;
  description: string;
  width: number;
  height: number;
  size: number;
  meta: {
    merge_method: string;
    merged: [];
  };
  groupLevels: GroupLevel[];
}

interface GroupLevel {
  color: string;
  description: string;
  label: string;
  name: string;
}

export default defineComponent({
  props: {
    id: {
      type: String,
      required: true,
      default: null,
    },
  },
  components: {
    MergeMethods,
  },
  setup(props) {
    // Data
    const valid = ref(false);
    const requiredRules = ref([
      (v: string) => !!v.trim() || 'Name is required',
    ]);
    const groupLevelHeaders = ref([
      {
        text: 'Name',
        value: 'name',
        sortable: true,
      },
      {
        text: 'Label',
        value: 'label',
        sortable: true,
      },
      {
        text: 'Description',
        value: 'description',
        sortable: false,
      },
      {
        text: 'Color',
        value: 'color',
        sortable: false,
      },
    ]);
    const method = ref(null) as Ref<string | null>;

    // Computed
    const dataset = computed((): Dataset => store.getters.dataset(props.id));
    const ready = computed((): boolean => store.getters.ready(props.id));
    const groupLevels = computed((): GroupLevel[] => dataset.value.groupLevels);
    const isMerged = computed((): boolean => store.getters.isMerged(props.id));
    const mergedDatasets = computed(() => {
      if (!isMerged.value) {
        return [];
      }
      const merged = dataset.value.meta.merged || [];
      return merged.map((d) => {
        const ds = store.getters.dataset(d);
        if (!ds) {
          return {
            id: d,
            name: 'Deleted Data Source',
            valid: false,
            description: '',
          };
        }
        return {
          id: ds.id,
          name: ds.name,
          description: ds.description,
          valid: store.getters.valid(ds.id),
        };
      });
    });
    // eslint-disable-next-line max-len
    const allDatasetsValid = computed(() => isMerged.value && mergedDatasets.value.every((d) => d.valid));

    // Methods
    const { formatSize } = sizeFormatter.methods;
    function setName(name: string) {
      if (!name.trim()) {
        return;
      }
      store.dispatch(SET_DATASET_NAME, { dataset_id: props.id, name: name.trim() });
    }
    function setDescription(description: string) {
      store.dispatch(SET_DATASET_DESCRIPTION, { dataset_id: props.id, description });
    }
    function changeGroupLevel(
      groupLevel: GroupLevel,
      change: {
        label?: string;
        description?: string;
        color?: string;
      },
    ) {
      const levels = groupLevels.value.map((level) => {
        if (level === groupLevel) {
          return { ...level, ...change };
        }
        return level;
      });
      store.dispatch(SET_DATASET_GROUP_LEVELS, { dataset_id: props.id, groupLevels: levels });
    }
    function remerge() {
      if (!allDatasetsValid.value) {
        return;
      }
      store.dispatch(REMERGE_DATASET, { dataset_id: props.id, method: method.value });
    }

    watch(dataset, (newValue) => {
      if (newValue && store.getters.isMerged(newValue.id)) {
        method.value = newValue.meta.merge_method;
      } else {
        method.value = null;
      }
    });

    if (!dataset.value) {
      // initialize the dataset to prevent NPE race conditions during slow loads
      store.commit(INTIALIZE_DATASET, { dataset_id: props.id });
      store.dispatch(LOAD_DATASET, { dataset_id: props.id });
    }
    if (dataset.value && store.getters.isMerged(dataset.value.id)) {
      method.value = dataset.value.meta.merge_method;
    }

    return {
      valid,
      requiredRules,
      groupLevelHeaders,
      method,
      dataset,
      ready,
      groupLevels,
      isMerged,
      mergedDatasets,
      allDatasetsValid,
      formatSize,
      setName,
      setDescription,
      changeGroupLevel,
      remerge,
    };
  },
});
</script>

<template>
  <v-layout
    class="data-source"
    row
    fill-height="fill-height"
  >
    <v-container
      v-if="dataset && ready"
      class="grow-overflow ma-0"
      grid-list-lg="grid-list-lg"
      fluid
    >
      <v-container
        class="pa-2"
        :style="{ height: 0 }"
      >
        <v-form v-model="valid">
          <v-text-field
            label="Data Source Name"
            :value="dataset.name"
            required
            :rules="requiredRules"
            @change="setName($event)"
          />
          <v-textarea
            label="Description"
            :value="dataset.description"
            @change="setDescription($event)"
          />
          <v-text-field
            label="Creation Date"
            :value="dataset.created.toISOString().slice(0, -1)"
            type="datetime-local"
            readonly
          />
          <v-text-field
            label="File Size"
            :value="formatSize(dataset.size)"
            readonly
          />
          <v-text-field
            label="File Dimensions"
            :value="`${dataset.width} x ${dataset.height}`"
            readonly
          />
          <v-list
            v-if="isMerged"
            subheader
          >
            <merge-methods v-model="method" />
            <v-subheader>
              <div class="grow">
                Merged Data Sources
              </div>
              <v-btn
                :disabled="!allDatasetsValid"
                @click="remerge()"
              >
                Remerge
              </v-btn>
            </v-subheader>
            <v-list-tile
              v-for="dataset in mergedDatasets"
              :key="dataset.id"
              class="plain"
            >
              <v-list-tile-content>
                <v-list-tile-title>{{ dataset.name }}</v-list-tile-title>
                <v-list-tile-sub-title
                  v-if="!dataset.valid"
                  color="error"
                >
                  Invalid Data source
                </v-list-tile-sub-title>
                <v-list-tile-sub-title
                  v-else
                  class="wrapped"
                >
                  {{ dataset.description || 'No Description' }}
                </v-list-tile-sub-title>
              </v-list-tile-content>
              <v-list-tile-action>
                <v-btn
                  :to="{ name: '', params: { id: dataset.id } }"
                  icon
                >
                  <v-icon>{{ $vuetify.icons.eye }}</v-icon>
                </v-btn>
              </v-list-tile-action>
            </v-list-tile>
          </v-list>
          <v-subheader>Groups</v-subheader>
          <v-data-table
            :headers="groupLevelHeaders"
            :items="groupLevels"
            item-key="name"
            hide-actions="hide-actions"
          >
            <template #items="props">
              <td>
                <v-text-field
                  placeholder="Name"
                  :value="props.item.name"
                  required
                  readonly
                />
              </td>
              <td>
                <v-text-field
                  placeholder="Label"
                  :value="props.item.label"
                  required
                  @change="changeGroupLevel(props.item, { label: $event })"
                />
              </td>
              <td>
                <v-text-field
                  placeholder="Description"
                  :value="props.item.description"
                  @change="changeGroupLevel(props.item, { description: $event })"
                />
              </td>
              <td>
                <input
                  placeholder="Color"
                  :value="props.item.color"
                  type="color"
                  required
                  @change="changeGroupLevel(props.item, { color: $event.currentTarget.value })"
                >
              </td>
            </template>
          </v-data-table>
        </v-form>
      </v-container>
    </v-container>
    <v-layout
      v-else
      justify-center="justify-center"
      align-center="align-center"
    >
      <v-progress-circular
        indeterminate
        size="100"
        width="5"
      />
      <h4 class="display-1 pa-3">
        Loading Data Set
      </h4>
    </v-layout>
  </v-layout>
</template>

<style scoped>
.plain >>> .v-list__tile {
  height: unset;
  align-items: flex-start;
}

.wrapped {
  white-space: pre;
}
</style>
