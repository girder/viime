<script lang="ts">
import {
  defineComponent, toRefs, PropType, computed,
} from '@vue/composition-api';
import ColorerOption from './ColorerOption.vue';
import useSample, { sampleProps } from './use/useSample';

interface Colorer {
  option: string | null;
  levels: {
    name: string;
    color: string[];
  };
  apply?: (row: string) => string | null;
}

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: 'Sample Color',
    },
    value: {
      type: Object as PropType<Colorer>,
      required: false,
      default: null,
    },
    ...sampleProps,
  },
  components: {
    ColorerOption,
  },
  setup(props, context) {
    const { options, categoricalMetaData, rowToIndex } = useSample(toRefs(props), context);
    function generateColorer(value: string) {
      if (!value) {
        return () => undefined;
      }
      const meta = categoricalMetaData.value.find((d) => d.value === value);
      if (!meta) {
        return () => undefined;
      }
      const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
      const toIndex = rowToIndex.value;
      return (column: string) => lookup.get(meta.data[toIndex(column)]);
    }
    function generateLevels(value: string) {
      if (!value || value === props.emptyOption) {
        return [];
      }
      return options.value.find((d) => d.value === value)?.options || [];
    }
    function changeValue(value: string) {
      const wrapper = {
        option: value,
        levels: generateLevels(value),
        apply: generateColorer(value),
      };
      context.emit('input', wrapper);
    }
    const validatedValue = computed(() => {
      if (props.value) {
        return props.value.option;
      }
      if (options.value.length === 0) {
        return null;
      }
      const v = options.value[0].value;
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
  <colorer-option
    :title="title"
    :disabled="disabled"
    :options="options"
    :value="validatedValue"
    @input="changeValue($event)"
  />
</template>
