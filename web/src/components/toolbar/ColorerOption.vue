<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

export interface IOptionGroup {
  name: string;
  value: string;
  options: {name: string, color?: string}[];
}

@Component
export default class ColorerOption extends Vue {
  @Prop({
    default: '',
  })
  readonly title!: string;

  @Prop({
    default: null,
  })
  readonly value!: string|null;

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

  get filterOptions() {
    const selected = this.options.find(d => d.value === this.value);
    return selected ? selected.options : [];
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
