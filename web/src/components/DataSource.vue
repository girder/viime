<script>
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import {
  SET_DATASET_NAME, SET_DATASET_DESCRIPTION, SET_DATASET_GROUP_LEVELS, REMERGE_DATASET,
} from '../store/actions.type';
import { loadDataset } from '../utils/mixins';
import { mergeMethods } from './NewMerge.vue';

export default {
  mixins: [loadDataset, sizeFormatter],
  data() {
    return {
      valid: false,
      requiredRules: [
        v => !!v.trim() || 'Name is required',
      ],
      groupLevelHeaders: [
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
      ],
      method: null,
      mergeMethods,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    groupLevels() { return this.dataset.groupLevels; },
    isMerged() { return this.$store.getters.isMerged(this.id); },
    mergedDatasets() {
      if (!this.isMerged) {
        return [];
      }
      const merged = this.dataset.meta.merged || [];
      return merged.map((d) => {
        const ds = this.$store.getters.dataset(d);
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
          valid: this.$store.getters.valid(ds.id),
        };
      });
    },
    allDatasetsValid() { return this.isMerged && this.mergedDatasets.every(d => d.valid); },
  },
  watch: {
    dataset(newValue) {
      if (newValue && this.$store.getters.isMerged(newValue.id)) {
        this.method = newValue.meta.merge_method;
      } else {
        this.method = null;
      }
    },
  },
  created() {
    if (this.dataset && this.$store.getters.isMerged(this.dataset.id)) {
      this.method = this.dataset.meta.merge_method;
    }
  },
  methods: {
    setName(name) {
      if (!name.trim()) {
        return;
      }
      this.$store.dispatch(SET_DATASET_NAME, { dataset_id: this.id, name: name.trim() });
    },
    setDescription(description) {
      this.$store.dispatch(SET_DATASET_DESCRIPTION, { dataset_id: this.id, description });
    },
    changeGroupLevel(groupLevel, change) {
      const levels = this.groupLevels.map((level) => {
        if (level === groupLevel) {
          return { ...level, ...change };
        }
        return level;
      });
      this.$store.dispatch(SET_DATASET_GROUP_LEVELS, { dataset_id: this.id, groupLevels: levels });
    },
    remerge() {
      if (!this.allDatasetsValid) {
        return;
      }
      this.$store.dispatch(REMERGE_DATASET, { dataset_id: this.id, method: this.method });
    },
  },
};
</script>

<template lang="pug">
v-layout.data-source(row, fill-height)
  v-container.grow-overflow.ma-0(grid-list-lg, fluid, v-if="dataset && ready")
    v-container.pa-2(:style="{height: 0}")
      v-form(v-model="valid")
        v-text-field(label="Data Source Name", :value="dataset.name", required,
            @change="setName($event)", :rules="requiredRules")
        v-textarea(label="Description", :value="dataset.description",
            @change="setDescription($event)")
        v-text-field(label="Creation Date", :value="dataset.created.toISOString().slice(0, -1)",
            type="datetime-local", readonly)
        v-text-field(label="File Size", :value="formatSize(dataset.size)",
            readonly)
        v-text-field(label="File Dimensions", :value="`${dataset.width} x ${dataset.height}`",
            readonly)

        v-list(subheader, v-if="isMerged")
          v-radio-group(v-model="method", label="Merge Method")
            v-radio(v-for="method in mergeMethods", :key="method.value",
                :label="method.label", :value="method.value")
          v-subheader
            .grow() Merged Data Sources
            v-btn(:disabled="!allDatasetsValid", @click="remerge()") Remerge

          v-list-tile.plain(v-for="dataset in mergedDatasets", :key="dataset.id")
            v-list-tile-content
              v-list-tile-title {{dataset.name}}
              v-list-tile-sub-title(v-if="!dataset.valid", color="error") Invalid Data source
              v-list-tile-sub-title.wrapped(v-else) {{dataset.description || 'No Description'}}
            v-list-tile-action
              v-btn(:to="{name: '', params: {id: dataset.id}}", icon)
                v-icon {{$vuetify.icons.eye}}

        v-subheader Groups
        v-data-table(:headers="groupLevelHeaders", :items="groupLevels", item-key="name",
            hide-actions)
          template(#items="props")
            td
              v-text-field(placeholder="Name", :value="props.item.name", required, readonly)
            td
              v-text-field(placeholder="Label", :value="props.item.label", required,
                  @change="changeGroupLevel(props.item, {label: $event})")
            td
              v-text-field(placeholder="Description", :value="props.item.description",
                  @change="changeGroupLevel(props.item, {description: $event})")
            td
              input(placeholder="Color", :value="props.item.color", type="color", required,
                  @change="changeGroupLevel(props.item, {color: $event.currentTarget.value})")

  v-layout(v-else, justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
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
