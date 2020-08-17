<script>
import Vue from 'vue';
import MetaboliteTable from './MetaboliteTable.vue';

export default Vue.extend({
  components: {
    MetaboliteTable,
  },

  props: {
    data: {
      type: Object,
      required: true,
      validator: (prop) => !prop || ('data' in prop && 'pairs' in prop),
    },
    threshold: {
      type: Number,
      required: false,
      default: 0.05,
    },
    value: { // string[]
      type: Array,
      required: true,
    },
    errorMsg: { // error message to display if ANOVA fails, if applicable
      type: String,
      default: '',
    },
  },

  computed: {
    items() {
      return (this.data && this.data.data) || [];
    },
    pairs() {
      return (this.data && this.data.pairs) || [];
    },
    headers() {
      return [
        {
          text: 'Metabolite',
          align: 'left',
          value: 'Metabolite',
          isLabel: true,
        },
        ...this.pairs.map((text) => ({ text, value: text })),
      ];
    },
  },
});
</script>

<template lang="pug">
metabolite-table(
    :headers="headers",
    :items="items",
    :no-data-available-msg="`Wilcoxon Test failed. ${errorMsg}`",
    :threshold="threshold",
    :value="value",
    @input="$emit('input', $event)")
</template>
