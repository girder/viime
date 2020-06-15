<script>
import FilterOption from './FilterOption.vue';
import metaboliteMixin from './mixins/metaboliteMixin';

// interface IGroup {
//   name: string;
//   color: string;
//   indices: number[];
//   columns: string[];
// }
// interface IMetaboliteFilter {
//   option: string | null;
//   filter: string[];
//   apply(column: string): boolean;
//   groupBy(columns: string[]): IGroup[];
// }

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
    value: { // IMetaboliteFilter
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
  watch: {
    selectionLookup() {
      // trigger update upon selection change
      if (this.value && this.value.option === 'selection') {
        this.changeValue(this.value);
      }
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
        return (column) => (isSelected(column) ? showSelected : showNotSelected);
      }
      const meta = this.categoricalMetaData.find((d) => d.value === value.option);
      const lookup = new Set(value.filter);
      const toIndex = this.columnToIndex;
      return (column) => lookup.has(meta.data[toIndex(column)]);
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
      const toIndex = this.columnToIndex;

      if (value.option === 'selection') {
        const isSelected = this.selectionLookup;
        const showSelected = value.filter.includes('selected');
        const showNotSelected = value.filter.includes('not-selected');
        const [selected, notSelected] = this.selectedOption[0].options;
        return (columns) => {
          const groups = [];
          if (showSelected) {
            const subset = columns.filter((column) => isSelected(column));
            groups.push({
              name: selected.name,
              color: selected.color,
              columns: subset,
              indices: subset.map((r) => toIndex(r)),
            });
          }
          if (showNotSelected) {
            const subset = columns.filter((column) => !isSelected(column));
            groups.push({
              name: notSelected.name,
              color: notSelected.color,
              columns: subset,
              indices: subset.map((r) => toIndex(r)),
            });
          }
          return groups;
        };
      }
      const meta = this.categoricalMetaData.find((d) => d.value === value.option);
      const lookup = new Set(value.filter);
      const options = meta.levels.filter((o) => lookup.has(o.name));
      return (columns) => options.map((v) => {
        const subset = columns.filter((column) => meta.data[toIndex(column)] === v.name);
        return {
          name: v.label,
          color: v.color,
          columns: subset,
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
