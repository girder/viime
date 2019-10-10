<script>

export default {
  data() {
    return {
      valid: false,
      requiredRules: [
        v => !!v.trim() || 'Name is required',
      ],
      name: 'Unnamed Merged Dataset',
      description: '',
      created: new Date(Date.now()),
      chosen: {},
    };
  },
  computed: {
    datasets() {
      return Object.values(this.$store.state.datasets);
    },
  },
  methods: {
    submit() {
      if (!this.$refs.form.validate()) {
        return;
      }
      // TODO
    },
  },
};
</script>

<template lang="pug">
v-form(v-model="valid", ref="form")
  v-container
    v-text-field(label="Data Source Name", v-model="name", required,
        :rules="requiredRules")
    v-textarea(label="Description", v-model="description")
    v-text-field(label="Creation Date", :value="created.toISOString().slice(0, -1)",
        type="datetime-local", readonly)

    v-list(subheader,two-line)
      v-subheader Data Sources
      v-list-tile(v-for="dataset in datasets", :key="dataset.id")
        v-list-tile-action
          v-checkbox(v-model="chosen[dataset.id]")
        v-list-tile-content()
          v-list-tile-title {{dataset.name}}
          v-list-tile-sub-title {{dataset.description || 'No Description'}}


    v-btn.right(@click="submit", :disabled="!valid", color="primary") create
    v-btn.right(to="/") cancel
</template>
