<script>
import FilterOption from './FilterOption.vue';
import sampleMixin from './mixins/sampleMixin';

// interface IGroup {
//   name: string;
//   color: string;
//   indices: number[];
//   rows: string[];
// }
// interface ISampleFilter {
//   option: string | null;
//   filter: string[];
//   apply(row: string): boolean;
//   groupBy(row string[]): IGroup[];
// }

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
    value: { // ISampleFilter
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
        filter: firstOption.options.map((d) => d.value),
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
      const meta = this.categoricalMetaData.find((d) => d.value === value.option);
      const lookup = new Set(value.filter);
      const toIndex = this.rowToIndex;
      return (row) => lookup.has(meta.data[toIndex(row)]);
    },
    generateGroupBy(value) {
      if (!value.option) {
        return (rows) => [{
          name: 'default',
          color: '#ffffff',
          rows,
          indices: rows.map((_, i) => i),
        }];
      }
      const meta = this.categoricalMetaData.find((d) => d.value === value.option);
      const lookup = new Set(value.filter);
      const options = meta.levels.filter((o) => lookup.has(o.name));
      const toIndex = this.rowToIndex;
      return (rows) => options.map((v) => {
        const subset = rows.filter((row) => meta.data[toIndex(row)] === v.name);
        return {
          name: v.label,
          color: v.color,
          rows: subset,
          indices: subset.map((r) => toIndex(r)),
        };
      });
    },
    changeValue(value) {
      value.apply = this.generateFilter(value);
      value.groupBy = this.generateGroupBy(value);
      this.$emit('input', value);
    },
  },
};
</script>

<template lang="pug">
filter-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
