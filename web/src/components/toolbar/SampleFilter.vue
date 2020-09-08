<script lang="ts">
import {
  PropType, defineComponent, toRefs, computed,
} from '@vue/composition-api';
import FilterOption from './FilterOption.vue';
import useSample, { sampleProps } from './use/useSample';

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
      default: 'Sample Filter',
    },
    value: {
      type: Object as PropType<Filter>,
      required: false,
      default: null,
    },
    ...sampleProps,
  },
  components: {
    FilterOption,
  },
  setup(props, context) {
    const { options, categoricalMetaData, rowToIndex } = useSample(toRefs(props), context);
    function generateFilter(value: Filter) {
      if (!value.option) {
        return () => true;
      }
      const meta = categoricalMetaData.value.find((d) => d.value === value.option);
      if (!meta) {
        return () => true;
      }
      const lookup = new Set(value.filter);
      const toIndex = rowToIndex.value;
      return (row: string) => lookup.has(meta.data[toIndex(row)]);
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
      const meta = categoricalMetaData.value.find((d) => d.value === value.option);
      if (!meta) {
        return (rows: string[]) => [{
          name: 'default',
          color: '#ffffff',
          rows,
          indices: rows.map((_, i) => i),
        }];
      }
      const lookup = new Set(value.filter);
      const levels = meta.levels.filter((o) => lookup.has(o.name));
      const toIndex = rowToIndex.value;
      return (rows: string[]) => levels.map((v) => {
        const subset = rows.filter((row) => meta.data[toIndex(row)] === v.name);
        return {
          name: v.label,
          color: v.color,
          rows: subset,
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
