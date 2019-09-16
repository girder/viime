<script>
import { format } from 'd3-format';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  extends: AnalyzeBaseVue,
  data() {
    return {
      key: 'anova',
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
      format: format('.2e'),
    };
  },
  computed: {
    items() {
      return this.results ? this.results.data : [];
    },
    pairs() {
      return this.results ? this.results.pairs : [];
    },
    headers() {
      // const groups = this.results ? this.results.groups : [];
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
  methods: {

  },
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block content
  v-data-table.elevation-1(:headers='headers', :items='items', disable-initial-sort,
      item-key='Metabolite')
    template(v-slot:items='props')
      td {{ props.item.Metabolite }}
      td.text-xs-right {{ format(props.item.Intercept) }}
      td.text-xs-right {{ format(props.item.Group) }}
      td.text-xs-right {{ format(props.item.Residuals) }}
      td.text-xs-right(v-for="p in pairs", :key="p") {{ format(props.item[p]) }}
</template>

<style scoped lang="scss">

</style>
