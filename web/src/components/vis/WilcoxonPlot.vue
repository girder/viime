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
      validator: prop => !prop || ('data' in prop),
    },
  },

  computed: {
    items() {
      return (this.data && this.data.data) || [];
    },
    headers() {
      return [
        {
          text: 'Metabolite',
          value: 'Metabolite',
        },
        {
          text: 'Wilcoxon',
          value: 'Wilcoxon',
        },
        {
          text: 'Bonferroni',
          value: 'Bonferroni',
        },
        {
          text: 'Hochberg',
          value: 'Hochberg',
        },
      ];
    },
  },
});
</script>

<template lang="pug">
metabolite-table(:headers="headers", :items="items")
</template>
