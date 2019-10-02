<script>
import { format } from 'd3-format';

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
    threshold: {
      type: Number,
      required: false,
      default: 0.05,
    },
  },

  data() {
    return {
      format: format('.4e'),
      pagination: {
        rowsPerPage: -1,
      },
    };
  },

  methods: {
    isInteresting(value) {
      return value < this.threshold;
    },
  },
};
</script>

<template lang="pug">
v-data-table.elevation-1.main(:headers="headers", :items="items", disable-initial-sort,
    item-key="Metabolite", :pagination.sync="pagination")
  template(v-slot:items="props")
    td.cell {{ props.item.Metabolite }}
    td.cell.text-xs-right(v-for="c in headers.slice(1)",
        :class="isInteresting(props.item[c.value]) ? 'highlight' : ''")
      | {{ format(props.item[c.value]) }}
</template>

<style scoped>
.highlight {
  background-color: #ffadad;
}

.main {
  height: 0;
}

.main >>> tr {
  height: 25px;
}
.main >>> td.cell {
  height: 25px;
  padding: 2px 7px;
}
</style>
