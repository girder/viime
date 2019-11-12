<script>
import { CREATE_MERGED_DATASET } from '../store/actions.type';
import MergeMethods, { DEFAULT_MERGE_METHOD } from './MergeMethods.vue';

export default {
  components: {
    MergeMethods,
  },
  data() {
    return {
      valid: false,
      requiredRules: [
        v => !!v.trim() || 'Name is required',
      ],
      selectedRules: [
        () => this.selected.length >= 2 || 'At least two data sources are required',
      ],
      name: 'Unnamed Merged Dataset',
      description: '',
      selected: [],
      method: DEFAULT_MERGE_METHOD,
      error: null,
    };
  },
  computed: {
    datasets() {
      return Object.values(this.$store.state.datasets).map(d => ({
        id: d.id,
        name: d.name,
        dataset: d,
        description: d.description,
        valid: this.$store.getters.valid(d.id),
      }));
    },
    mergeInfo() {
      const selected = this.datasets.filter(d => this.selected.includes(d.id)
                                                 && d.dataset.validatedMeasurements);
      if (selected.length < 2) {
        return {
          intersection: 0,
          union: 0,
          w: false,
        };
      }
      // check overlap of their row identifiers

      const rowNames = selected.map(d => new Set(d.dataset.validatedMeasurements.rowNames));

      const union = rowNames.reduce((acc, n) => {
        n.forEach(v => acc.add(v));
        return acc;
      }, new Set());

      const intersection = Array.from(rowNames[0]).filter(v => rowNames.every(r => r.has(v)));

      return {
        intersection: intersection.length,
        union: union.size,
        w: (intersection.length / union.size) < 0.8,
      };
    },

  },
  methods: {
    rank(dataset) {
      return this.selected.includes(dataset.id) ? String(this.selected.indexOf(dataset.id) + 1) : ' ';
    },
    async submit(evt) {
      evt.preventDefault();
      evt.stopPropagation();

      if (!this.$refs.form.validate() || !this.valid) {
        return;
      }
      this.error = null;
      try {
        const dataset = await this.$store.dispatch(CREATE_MERGED_DATASET, {
          name: this.name,
          description: this.description,
          datasets: this.selected,
          method: this.method,
        });

        this.$router.push({
          name: 'Clean Up Table',
          params: { id: dataset.id },
        });
      } catch (error) {
        this.error = error;
      }
    },
  },
};
</script>

<template lang="pug">
v-form(v-model="valid", ref="form", @submit="submit")
  v-container
    .v-messages.theme--light.error--text(v-if="error")
      .v-messages__wrapper
        .v-messages__message {{error}}

    v-text-field(label="Data Source Name", v-model="name", required,
        :rules="requiredRules")
    v-textarea(label="Description", v-model="description")
    merge-methods(v-model="method")

    v-list(subheader)
      v-subheader Data Sources
      v-list-tile.plain(v-for="(dataset, index) in datasets", :key="dataset.id")
        v-list-tile-action
          v-checkbox.numbered(v-model="selected", :value="dataset.id", :rules="selectedRules",
              :disabled="!dataset.valid", :prepend-icon="rank(dataset)")
        v-list-tile-content
          v-list-tile-title {{dataset.name}}
          v-list-tile-sub-title(v-if="!dataset.valid", color="error") Invalid Data source
          v-list-tile-sub-title.wrapped(v-else) {{dataset.description || 'No Description'}}
    .v-messages.theme--light.error--text(v-if="!(selected.length >= 2)")
      .v-messages__wrapper
        .v-messages__message At least two data sources are required
    .v-messages.theme--light.bigger(v-if="selected.length >= 2")
      .v-messages__wrapper(:class="{'warning--text': mergeInfo.w}")
        .v-messages__message
          | {{ mergeInfo.intersection }} out of {{ mergeInfo.union }} samples will be merged

    v-btn.right(type="submit", :disabled="!valid",
        color="primary") create
    v-btn.right(:to="{name: 'App'}") cancel
</template>

<style scoped>
.numbered >>> .v-input__prepend-outer {
  margin-right: 0;
  margin-left: -10px;
}

.numbered >>> .v-input__icon--prepend > .v-icon {
  font-size: unset;
  font-feature-settings: unset;
  font-style: normal;
}

.bigger {
  font-size: 16px;
}

.plain >>> .v-list__tile {
  height: unset;
  align-items: flex-start;
}

.wrapped {
  white-space: pre;
}
</style>
