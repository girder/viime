<script>
import { format } from 'd3-format';
import Vue from 'vue';

export default {

  props: {
    data: {
      type: Array,
      required: true,
    },
  },

  data() {
    return {
      format: format('.2e')
    };
  },

  computed: {
    items(){
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
          value: 'Metabolite'
        },
        {
          text: 'Intercept',
          value: 'Intercept'
        },
        {
          text: 'Group',
          value: 'Group'
        },
        {
          text: 'Residuals',
          value: 'Residuals'
        },
        ...this.pairs.map(text => ({ text, value: text }))
      ];
    }
  }
}
</script>

<template lang="pug">
analyze-wrapper(:id="id", :name="name", toolbar-hidden)
  v-data-table.elevation-1(:headers="headers", :items="items", disable-initial-sort,
      item-key="Metabolite")
    template(v-slot:items="props")
      td {{ props.item.Metabolite }}
      td.text-xs-right {{ format(props.item.Intercept) }}
      td.text-xs-right {{ format(props.item.Group) }}
      td.text-xs-right {{ format(props.item.Residuals) }}
      td.text-xs-right(v-for="p in pairs", :key="p") {{ format(props.item[p]) }}
</template>
