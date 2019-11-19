<script lang="ts">
import {
  Component, Prop, Mixins, Watch,
} from 'vue-property-decorator';
import ColorerOption from './ColorerOption.vue';
import MetaboliteMixin from './mixins/metaboliteMixin';
import { colors } from '../../utils/constants';

export interface IMetaboliteColorerValue {
  option: string | null,
  levels: {name: string, color: string}[];
  apply(column: string): string | null;
}

@Component({
  components: {
    ColorerOption,
  },
})
export default class MetaboliteColorer extends Mixins(MetaboliteMixin) {
  @Prop({
    default: 'Metabolite Color',
  })
  readonly title!: string;

  @Prop({
    default: null,
  })
  readonly value!: IMetaboliteColorerValue;

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

  @Watch('selectionLookup')
  watchSelectionLookup() {
    // trigger update upon selection change
    if (this.value && this.value.option === 'selection') {
      this.changeValue('selection');
    }
  }

  private generateColorer(value: string | null) {
    if (!value || value === this.emptyOption) {
      return () => null;
    }
    if (value === 'selection') {
      const isSelected = this.selectionLookup;
      return (column: string) => (isSelected(column) ? colors.selected : this.notSelectedColor);
    }
    const meta = this.categoricalMetaData.find(d => d.name === value)!;
    const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
    const toIndex = this.columnToIndex;
    return (column: string) => lookup.get(String(meta.data[toIndex(column)]));
  }

  private generateLevels(value: string | null) {
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
