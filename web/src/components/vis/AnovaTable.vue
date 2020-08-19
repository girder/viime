<script lang="ts">
import { PropType, defineComponent, computed } from '@vue/composition-api';
import MetaboliteTable, { Item } from './MetaboliteTable.vue';

interface Data {
  data?: Array<Item>;
  pairs?: Array<string>;
}

export default defineComponent({
  props: {
    data: {
      type: Object as PropType<Data>,
      required: false,
    },
    threshold: {
      type: Number,
      default: 0.05,
    },
    value: {
      type: Array as PropType<Array<string>>,
      required: true,
    },
    errorMsg: { // error message to display if ANOVA fails, if applicable
      type: String,
      default: '',
    },
  },
  components: {
    MetaboliteTable,
  },

  setup(props) {
    const items = computed(() => (props.data && props.data.data) || []);
    const pairs = computed(() => (props.data && props.data.pairs) || []);
    const headers = computed(() => [
      {
        text: 'Metabolite',
        align: 'left',
        value: 'Metabolite',
        isLabel: true,
      },
      {
        text: 'Group',
        value: 'Group',
        isLabel: true,
      },
      ...pairs.value.map((text) => ({ text, value: text })),
    ]);
    return {
      items,
      pairs,
      headers,
    };
  },
});
</script>

<template>
  <metabolite-table
    :headers="headers"
    :items="items"
    :threshold="threshold"
    :value="value"
    :no-data-available-msg="`ANOVA failed. ${errorMsg}`"
    @input="$emit('input', $event)"
  />
</template>
