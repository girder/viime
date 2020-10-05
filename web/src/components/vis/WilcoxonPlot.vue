<script lang="ts">
import { PropType, defineComponent, computed } from '@vue/composition-api';
import MetaboliteTable, { Item } from './MetaboliteTable.vue';

interface Data {
  data?: Item[];
  pairs?: string[];
}

export default defineComponent({
  props: {
    data: {
      type: Object as PropType<Data>,
      required: true,
    },
    threshold: {
      type: Number,
      default: 0.05,
    },
    value: {
      type: Array as PropType<string[]>,
      required: true,
    },
    errorMsg: { // error message to display if Wilcoxon Test fails, if applicable
      type: String,
      default: '',
    },
  },
  components: {
    MetaboliteTable,
  },
  setup(props) {
    const items = computed(() => (props.data?.data) || []);
    const pairs = computed(() => (props.data?.pairs) || []);
    const headers = computed(() => [
      {
        text: 'Metabolite',
        align: 'left',
        value: 'Metabolite',
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
    :no-data-available-msg="`Wilcoxon Test failed. ${errorMsg}`"
    @input="$emit('input', $event)"
  />
</template>
