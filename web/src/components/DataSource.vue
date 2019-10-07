<script>
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import { SET_DATASET_NAME, SET_DATASET_DESCRIPTION, SET_DATASET_GROUP_LEVELS } from '../store/actions.type';
import { loadDataset } from '../utils/mixins';

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
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    groupLevels() { return this.dataset.groupLevels; },
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
  },
};
</script>

<template lang="pug">
v-layout.data-source(row, fill-height)
  v-container.grow-overflow.ma-0(grid-list-lg, fluid, v-if="dataset && ready")
    v-container.pa-2
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
