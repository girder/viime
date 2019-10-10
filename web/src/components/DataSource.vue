<script>
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import { SET_DATASET_NAME, SET_DATASET_DESCRIPTION } from '../store/actions.type';
import { loadDataset } from '../utils/mixins';

export default {
  mixins: [loadDataset, sizeFormatter],
  data() {
    return {
      valid: false,
      requiredRules: [
        v => !!v.trim() || 'Name is required',
      ],
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
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

  v-layout(v-else, justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
</template>
