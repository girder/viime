<script>
import FilterOption from './FilterOption.vue';
import sampleMixin from './mixins/sampleMixin';

export default {
  components: {
    FilterOption,
  },
  mixins: [sampleMixin],
  props: {
    title: {
      type: String,
      required: false,
      default: 'Sample Filter',
    },
    value: { // {option: string | null, filter: string[], apply(row: string) => boolean}
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
      const meta = this.categoricalMetaData.find(d => d.value === value.option);
      const lookup = new Set(value.filter);
      const toIndex = this.rowToIndex;
      return row => lookup.has(meta.data[toIndex(row)]);
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
