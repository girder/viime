<script>
import { CREATE_MERGED_DATASET } from '../store/actions.type';

export const mergeMethods = [
  {
    value: 'simple',
    label: 'Simple',
  },
  {
    value: 'clean',
    label: 'Clean PCA',
  },
];

export default {
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
      mergeMethods,
      method: mergeMethods[0].value,
      error: null,
    };
  },
  computed: {
    datasets() {
      return Object.values(this.$store.state.datasets).map(d => ({
        id: d.id,
        name: d.name,
        description: d.description,
        valid: this.$store.getters.valid(d.id),
      }));
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
    v-radio-group(v-model="method", label="Merge Method")
      v-radio(v-for="method in mergeMethods", :key="method.value",
          :label="method.label", :value="method.value")

    v-list(subheader, two-line)
      v-subheader Data Sources
      v-list-tile(v-for="(dataset, index) in datasets", :key="dataset.id")
        v-list-tile-action
          v-checkbox.numbered(v-model="selected", :value="dataset.id", :rules="selectedRules",
              :disabled="!dataset.valid", :prepend-icon="rank(dataset)")
        v-list-tile-content
          v-list-tile-title {{dataset.name}}
          v-list-tile-sub-title(v-if="!dataset.valid", color="error") Invalid Data source
          v-list-tile-sub-title(v-else) {{dataset.description || 'No Description'}}
    .v-messages.theme--light.error--text(v-if="!(selected.length >= 2)")
      .v-messages__wrapper
        .v-messages__message At least two data sources are required

    v-btn.right(type="submit", :disabled="!valid",
        color="primary") create
    v-btn.right(to="/") cancel
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
</style>
