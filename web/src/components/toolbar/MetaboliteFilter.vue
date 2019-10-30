<script>
import FilterOption from './FilterOption.vue';
import metaboliteMixin from './mixins/metaboliteMixin';

export default {
  components: {
    FilterOption,
  },
  mixins: [metaboliteMixin],
  props: {
    title: {
      type: String,
      required: false,
      default: 'Metabolite Filter',
    },
    value: { // {option: string | null, filter: string[], apply(column: string) => boolean}
      type: Object,
      required: false,
      default: null,
    },
  },
  computed: {
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
        option: firstOption.value,
        filter: firstOption.options.map(d => d.value),
      };
      this.changeValue(v);
      return v;
    },
  },
  methods: {
    generateFilter(value) {
      if (!value.option) {
        return () => true;
      }
      if (value.option === 'selection') {
        const isSelected = this.selectionLookup;
        const showSelected = value.filter.includes('selected');
        const showNotSelected = value.filter.includes('not-selected');
        return column => (isSelected(column) ? showSelected : showNotSelected);
      }
      const meta = this.categoricalMetaData.find(d => d.value === value.option);
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
