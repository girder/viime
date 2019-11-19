<script lang="ts">
import {
  Component, Prop, Mixins,
} from 'vue-property-decorator';
import ColorerOption from './ColorerOption.vue';
import SampleMixin from './mixins/sampleMixin';

export interface ISampleColorerValue {
  option: string | null,
  levels: {name: string, color: string}[];
  apply(row: string): string | null;
}

@Component({
  components: {
    ColorerOption,
  },
})
export default class SampleColorer extends Mixins(SampleMixin) {
  @Prop({
    default: 'Sample Color',
  })
  readonly title!: string;

  @Prop({
    default: null,
  })
  readonly value!: ISampleColorerValue;

  get validatedValue() {
    if (this.value) {
      return this.value.option;
    }
    if (this.options.length === 0) {
      return null;
    }
    const v = this.options[0].value;
    this.changeValue(v);
    return v;
  }

  generateColorer(value: string | null) {
    if (!value) {
      return () => null;
    }
    const meta = this.categoricalMetaData.find(d => d.value === value)!;
    const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
    const toIndex = this.rowToIndex;
    return (row: string) => lookup.get(String(meta.data[toIndex(row)]))!;
  }

  generateLevels(value: string | null) {
    if (!value || value === this.emptyOption) {
      return [];
    }
    return this.options.find(d => d.value === value)!.options;
  }

  changeValue(value: string | null) {
    const wrapper = {
      option: value,
      levels: this.generateLevels(value),
      apply: this.generateColorer(value),
    };
    this.$emit('input', wrapper);
  }
}
</script>

<template lang="pug">
colorer-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
