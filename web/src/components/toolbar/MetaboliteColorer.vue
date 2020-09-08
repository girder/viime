<script lang="ts">
import {
  PropType, defineComponent, computed, watch, toRefs,
} from '@vue/composition-api';
import ColorerOption from './ColorerOption.vue';
import { colors } from '../../utils/constants';
import useMetabolite, { metaboliteProps } from './use/useMetabolite';

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
      default: 'Metabolite Color',
    },
    value: {
      type: Object as PropType<Colorer>,
      required: false,
      default: null,
    },
    ...metaboliteProps,
  },
  components: {
    ColorerOption,
  },
  setup(props, context) {
    const {
      options,
      selectionLookup,
      categoricalMetaData,
      columnToIndex,
    } = useMetabolite(toRefs(props), context);
    function generateColorer(value: string) {
      if (!value || value === props.emptyOption) {
        return () => null;
      }
      if (value === 'selection') {
        const isSelected = selectionLookup.value;
        return (column: string) => (isSelected(column) ? colors.selected : props.notSelectedColor);
      }
      const meta = categoricalMetaData.value.find((d) => d.name === value);
      if (!meta) {
        return () => null;
      }
      const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
      const toIndex = columnToIndex.value;
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
    watch(selectionLookup, () => {
      // trigger update upon selection change
      if (props.value?.option === 'selection') {
        changeValue('selection');
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
  <colorer-option
    :title="title"
    :disabled="disabled"
    :options="options"
    :value="validatedValue"
    @input="changeValue($event)"
  />
</template>
