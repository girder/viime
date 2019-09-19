<script>
import { format } from 'd3-format';

const RELEVANT_PVALUE = 0.05;

export default {

  props: {
    items: {
      type: Array,
      required: true,
    },
    headers: {
      type: Array,
      required: true,
    },
  },

  data() {
    return {
      format: format('.2e'),
    };
  },

  methods: {
    isInteresting(value) {
      return value < RELEVANT_PVALUE;
    },
  },
};
</script>

<template lang="pug">
v-data-table.elevation-1(:headers="headers", :items="items", disable-initial-sort,
    item-key="Metabolite")
  template(v-slot:items="props")
    td {{ props.item.Metabolite }}
    td.text-xs-right(v-for="c in headers.slice(1)",
       :class="isInteresting(props.item[c.value]) ? 'highlight' : ''")
         | {{ format(props.item[c.value]) }}
</template>

<style lang="scss" scoped>
.highlight {
  background-color: #ffadad;
}
</style>
