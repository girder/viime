<script>
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  extends: AnalyzeBaseVue,
  data() {
    return {
      key: 'anova',
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
  computed: {
    ddd() {
      return JSON.stringify(this.results ? this.results.data : null);
    },
  },
  methods: {

  },
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block content
  | Test {{ ddd }}
</template>

<style scoped lang="scss">

</style>
