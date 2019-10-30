<script>
import FilterOption from './FilterOption.vue';
import { colors } from '../../utils/constants';

export default {
  components: {
    FilterOption,
  },
  props: {
    title: {
      type: String,
      required: false,
      default: 'Metabolite Filter',
    },
    dataset: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
    },
    value: { // {option: string | null, filter: string[], apply(column: string) => boolean}
      type: Object,
      required: false,
      default: null,
    },
    hideSelection: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    columnToIndex() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return () => -1;
      }
      const m = new Map(this.dataset.validatedMeasurements.columnNames.map((name, i) => [name, i]));
      return column => (m.has(column) ? m.get(column) : -1);
    },
    selectionLookup() {
      const selected = new Set((this.dataset && this.dataset.selectedColumns) || []);
      return name => selected.has(name);
    },
    countSelected() {
      return (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.dataset.validatedMeasurements) {
        return 0;
      }
      return this.dataset.validatedMeasurements.columnNames.length - this.countSelected;
    },
    categoricalMetaData() {
      const metaData = this.dataset.validatedMeasurementsMetaData;

      return metaData ? metaData.rowNames.map((name, i) => ({
        name,
        data: metaData.data[i],
        i,
        ...metaData.rowMetaData[i],
      })).filter(d => d.subtype === 'categorical') : [];
    },

    options() {
      const s = this.hideSelection ? [] : [{
        name: 'Selection',
        options: [
          {
            name: `Selected (${this.countSelected})`,
            value: 'selected',
            color: colors.selected,
          },
          {
            name: `Not Selected (${this.countNotSelected})`,
            value: 'not-selected',
            color: colors.notSelected,
          },
        ],
      }];
      return [
        ...s,
        ...this.categoricalMetaData.map(({ name, levels }) => ({
          name,
          options: levels.map(d => ({ name: d.label, value: d.name, color: d.color })),
        })),
      ];
    },
    validatedValue() {
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
        option: firstOption.name,
        filter: firstOption.options.map(d => d.value),
      };
      v.apply = this.generateFilter(v);
      return v;
    },
  },
  watch: {
    dataset(newValue, oldValue) {
      const newId = newValue ? newValue.id : '';
      const oldId = oldValue ? oldValue.id : '';
      if (newId !== oldId && this.value) {
        console.log('reset filter');
        this.$emit('input', null);
      }
    },
  },
  methods: {
    generateFilter(value) {
      if (!value.option) {
        return () => true;
      }
      if (value.option === 'Selection') {
        const isSelected = this.selectionLookup;
        const showSelected = value.filter.includes('selected');
        const showNotSelected = value.filter.includes('not-selected');
        return column => (isSelected(column) ? showSelected : showNotSelected);
      }
      const meta = this.categoricalMetaData.find(d => d.name === value.option);
      const lookup = new Set(value.filter);
      const toIndex = this.columnToIndex;
      return column => lookup.has(meta.data[toIndex(column)]);
    },
    changeValue(value) {
      value.apply = this.generateFilter(value);
      this.$emit('input', value);
    },
  },
};
</script>

<template lang="pug">
filter-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
