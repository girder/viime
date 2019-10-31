<script>
export default {
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    value: { // {option: string | null, filter: string[]}
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
    },
    options: { // {name: string, options: {name: string, color?: string, value: string}[]}[]
      type: Array,
      required: true,
    },
  },
  computed: {
    showSelect() {
      return !this.value || this.options.length > 1;
    },
    selected: {
      get() {
        return this.value ? this.value.option : null;
      },
      set(value) {
        if (!value) {
          this.$emit('input', { option: null, filter: [] });
        } else {
          const selected = this.options.find(d => d.value === value);
          this.$emit('input', { option: value, filter: selected.options.map(d => d.value) });
        }
      },
    },
    filterOptions() {
      const selected = this.options.find(d => d.value === this.selected);
      return selected ? selected.options : [];
    },
    filter: {
      get() {
        return this.value ? this.value.filter : [];
      },
      set(values) {
        this.$emit('input', { ...this.value, filter: values });
      },
    },
    hasOptions() {
      if (this.options.length === 0) {
        return false;
      }
      if (this.options.length === 1 && !this.options[0].value) {
        return false;
      }
      return true;
    },
  },
};
</script>

<template lang="pug">
div(v-if="hasOptions")
  v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
    v-toolbar-title
      slot(name=title) {{title}}

  v-card.mx-3(flat)
    v-card-actions(style="display: block")
      v-select.my-0(v-model="selected", v-if="showSelect",
          hide-details, :disabled="disabled",
          :items="options", item-text="name")
      v-checkbox.my-0.option(v-model="filter",
          v-for="o in filterOptions", :key="o.name",
          :label="o.name", :value="o.value", :title="o.name",
          hide-details, :color="o.color")
</template>

<style scoped>
.option {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
