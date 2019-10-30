<script>
export default {
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    value: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
    },
    options: { // {name: string, options: {name: string, color?: string}[]}[]
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
        this.$emit('input', value);
      },
    },
    filterOptions() {
      const selected = this.options.find(d => d.name === this.selected);
      return selected ? selected.options : [];
    },
  },
};
</script>

<template lang="pug">
div(v-if="options.length > 0")
  v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
    v-toolbar-title
      slot(name=title) {{title}}

  v-card.mx-3(flat)
    v-card-actions(style="display: block")
      v-select.my-0(v-model="selected", v-if="showSelect",
          hide-details, :disabled="disabled",
          :items="options", item-text="name")
      .my-0(v-for="o in filterOptions", :key="o.name")
        v-icon(:color="o.color") {{ }}
        {{ o.name }}
</template>