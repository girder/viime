<script lang="ts">
import {
  PropType, computed, defineComponent, watch, toRefs,
} from '@vue/composition-api';
import FilterOption from './FilterOption.vue';
import useMetabolite, { metaboliteProps } from './use/useMetabolite';

interface Group {
  name: string;
  color: string;
  indices: number[];
  columns?: string[];
  rows?: string[];
}
interface Filter {
  option: string | null;
  filter: string[];
  apply?: (column: string) => boolean;
  groupBy?: (columns: string[]) => Group[];
}

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: 'Metabolite Filter',
    },
    value: {
      type: Object as PropType<Filter>,
      required: false,
      default: null,
    },
    ...metaboliteProps,
  },
  components: {
    FilterOption,
  },
  setup(props, context) {
    const {
      options,
      selectionLookup,
      categoricalMetaData,
      columnToIndex,
      selectedOption,
    } = useMetabolite(toRefs(props), context);
    function generateFilter(value: Filter) {
      if (!value.option) {
        return () => true;
      }
      if (value.option === 'selection') {
        const isSelected = selectionLookup.value;
        const showSelected = value.filter.includes('selected');
        const showNotSelected = value.filter.includes('not-selected');
        return (column: string) => (isSelected(column) ? showSelected : showNotSelected);
      }
      const meta = categoricalMetaData.value.find((d) => d.value === value.option);
      if (!meta) {
        return () => true;
      }
      const lookup = new Set(value.filter);
      const toIndex = columnToIndex.value;
      return (column: string) => lookup.has(meta.data[toIndex(column)]);
    }
    function generateGroupBy(value: Filter) {
      if (!value.option) {
        return (rows: string[]) => [{
          name: 'default',
          color: '#ffffff',
          rows,
          indices: rows.map((_, i) => i),
        }];
      }
      const toIndex = columnToIndex.value;

      if (value.option === 'selection') {
        const isSelected = selectionLookup.value;
        const showSelected = value.filter.includes('selected');
        const showNotSelected = value.filter.includes('not-selected');
        const [selected, notSelected] = selectedOption.value[0].options;
        return (columns: string[]) => {
          const groups: Group[] = [];
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
      const meta = categoricalMetaData.value.find((d) => d.value === value.option);
      if (!meta) {
        return () => [];
      }
      const lookup = new Set(value.filter);
      const levels = meta.levels.filter((o) => lookup.has(o.name));
      return (columns: string[]) => levels.map((v) => {
        const subset = columns.filter((column) => meta.data[toIndex(column)] === v.name);
        return {
          name: v.label,
          color: v.color,
          columns: subset,
          indices: subset.map((r) => toIndex(r)),
        };
      });
    }
    function changeValue(value: Filter) {
      value.apply = generateFilter(value);
      value.groupBy = generateGroupBy(value);
      context.emit('input', value);
    }
    const validatedValue = computed(() => {
      if (props.value) {
        return props.value;
      }
      if (options.value.length === 0) {
        return {
          option: null,
          filter: [],
          apply: () => true,
        };
      }
      const firstOption = options.value[0];
      const v = {
        option: firstOption.value,
        filter: firstOption.options.map((d) => d.value),
      };
      changeValue(v);
      return v;
    });
    watch(selectionLookup, () => {
      // trigger update upon selection change
      if (props.value?.option === 'selection') {
        changeValue(props.value);
      }
    });
    return {
      options,
      validatedValue,
      changeValue,
    };
  },
});
</script>

<template>
  <filter-option
    :title="title"
    :disabled="disabled"
    :options="options"
    :value="validatedValue"
    @input="changeValue($event)"
  />
</template>
