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
      validator: prop => !prop || ('data' in prop && 'pairs' in prop),
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
          value: 'Metabolite',
        },
        ...this.pairs.map(text => ({ text, value: text })),
      ];
    },
  },
});
</script>

<template lang="pug">
metabolite-table(:headers="headers", :items="items", :threshold="threshold",
    :value="value", @input="$emit('input', $event)")
</template>
