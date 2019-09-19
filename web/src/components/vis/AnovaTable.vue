<script>
import { format } from 'd3-format';
import MetaboliteTable from './MetaboliteTable.vue';

export default {

  components: {
    MetaboliteTable,
  },

  props: {
    data: {
      type: Object,
      validator: prop => !prop || ('data' in prop && 'pairs' in prop),
      required: true,
    },
  },

  data() {
    return {
      format: format('.2e'),
    };
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
        },
        {
          text: 'Intercept',
          value: 'Intercept',
        },
        {
          text: 'Group',
          value: 'Group',
        },
        {
          text: 'Residuals',
          value: 'Residuals',
        },
        ...this.pairs.map(text => ({ text, value: text })),
      ];
    },
  },
};
</script>

<template lang="pug">
metabolite-table(:headers="headers", :items="items")
</template>
