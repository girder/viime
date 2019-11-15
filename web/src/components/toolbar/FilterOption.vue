<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

export interface IOptionGroup {
  name: string;
  value: string;
  options: {name: string, color?: string, value: string}[];
}

@Component
export default class FilterOption extends Vue {
   @Prop({
     default: '',
   })
  readonly title!: string;

  @Prop({
    required: true,
  })
  readonly value!: {option: string|null, filter: string[]};

  @Prop({
    default: false,
  })
  disabled!: boolean;

  @Prop({
    required: true,
  })
  options!: IOptionGroup[];

  get showSelect() {
    return !this.value || this.options.length > 1;
  }

  get selected() {
    return this.value ? this.value.option : null;
  }

  set selected(value: string | null) {
    if (!value) {
      this.$emit('input', { option: null, filter: [] });
    } else {
      const selected = this.options.find(d => d.value === value)!;
      this.$emit('input', { option: value, filter: selected.options.map(d => d.value) });
    }
  }

  get filterOptions() {
    const selected = this.options.find(d => d.value === this.selected);
    return selected ? selected.options : [];
  }

  get filter(): string[] {
    return this.value ? this.value.filter : [];
  }

  set filter(values: string[]) {
    this.$emit('input', { ...this.value, filter: values });
  }

  get hasOptions() {
    if (this.options.length === 0) {
      return false;
    }
    if (this.options.length === 1 && !this.options[0].value) {
      return false;
    }
    return true;
  }
}
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
