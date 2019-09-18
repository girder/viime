<script>
import Vue from 'vue';

export default Vue.extend({
  props: {
    dataset: {
      required: true,
      type: Object,
    },
  },
  data() {
    return {
      label: this.dataset.label,
      description: this.dataset.meta.description || '',
    };
  },
  watch: {
    dataset(newValue) {
      this.label = newValue.label;
      this.description = newValue.meta.description || '';
    },
  },
  methods: {
    cancel() {
      this.$emit('submit', null);
    },
    submit() {
      this.$emit('submit', {
        label: this.label,
        description: this.description,
      });
    },
  },
});
</script>
<template lang="pug">
v-dialog(value="true", max-width="300", persistent)
  v-card
    v-card-title.headline Edit Data Source "{{dataset.label}}"

    v-card-text
      v-text-field(label="Name", v-model="label", required)
      v-textarea(label="Description", v-model="description")

    v-card-actions
      v-spacer
      v-btn(@click="cancel()") Cancel
      v-btn(@click="submit()") Save
</template>
<style lang="scss" scoped>

</style>
