<script>
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
          text: 'Group',
          value: 'Group',
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
