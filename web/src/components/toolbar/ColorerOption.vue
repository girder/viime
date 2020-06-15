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
      required: false,
      default: null,
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
    filterOptions() {
      const selected = this.options.find((d) => d.value === this.value);
      return selected ? selected.options : [];
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
      v-select.my-0(:value="value", v-if="showSelect",
          hide-details, :disabled="disabled",
          @change="$emit('input', $event)",
          :items="options", item-text="name")
      .my-0.option(v-for="o in filterOptions", :key="o.name", :title="o.name")
        v-icon(:color="o.color") {{ $vuetify.icons.square }}
        | {{ o.name }}
</template>

<style scoped>
.option {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
