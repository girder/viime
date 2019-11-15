<script lang="ts">
import {
  Component, Vue, Prop, Mixins, Watch,
} from 'vue-property-decorator';
import FilterOption from './FilterOption.vue';
import SampleMixin from './mixins/sampleMixin';

export interface IGroup {
  name: string;
  color: string;
  indices: number[];
  rows: string[];
}
interface IFilterValueBase {
  option: string | null,
  filter: string[];
}

export interface ISampleFilterValue {
  option: string | null;
  filter: string[];
  apply(row: string): boolean;
  groupBy(row: string[]): IGroup[];
}

@Component({
  components: {
    FilterOption,
  },
})
export default class SampleFilter extends Mixins(SampleMixin) {
  @Prop({
    default: 'Sample Filter',
  })
  readonly title!: string;

  @Prop({
    default: null,
  })
  readonly value!: ISampleFilterValue;

  get validatedValue() {
    if (this.value) {
      return this.value;
    }
    if (this.options.length === 0) {
      return {
        option: null,
        filter: [],
        apply: () => true,
      };
    }
    const firstOption = this.options[0];
    const v = {
      option: firstOption.value,
      filter: firstOption.options.map(d => d.value),
    };
    this.changeValue(v);
    return v;
  }

  generateFilter(value: IFilterValueBase): ((row: string) => boolean) {
    if (!value.option) {
      return () => true;
    }
    const meta = this.categoricalMetaData.find(d => d.value === value.option)!;
    const lookup = new Set(value.filter);
    const toIndex = this.rowToIndex;
    return row => lookup.has(String(meta.data[toIndex(row)]));
  }

  generateGroupBy(value: IFilterValueBase): ((rows: string[]) => IGroup[]) {
    if (!value.option) {
      return (rows: string[]) => [{
        name: 'default',
        color: '#ffffff',
        rows,
        indices: rows.map((_, i) => i),
      }];
    }
    const meta = this.categoricalMetaData.find(d => d.value === value.option)!;
    const lookup = new Set(value.filter);
    const options = meta.levels.filter(o => lookup.has(o.name));
    const toIndex = this.rowToIndex;
    return (rows: string[]) => options.map((v) => {
      const subset = rows.filter(row => meta.data[toIndex(row)] === v.name);
      return {
        name: v.label || v.name,
        color: v.color,
        rows: subset,
        indices: subset.map(r => toIndex(r)),
      };
    });
  }

  changeValue(value: Partial<ISampleFilterValue> & IFilterValueBase) {
    value.apply = this.generateFilter(value);
    value.groupBy = this.generateGroupBy(value);
    this.$emit('input', value);
  }
}
</script>

<template lang="pug">
filter-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
