<script>
import { scaleSequential } from 'd3-scale';
import { interpolateGreys } from 'd3-scale-chromatic';
import { format } from 'd3-format';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  components: {
  },
  extends: AnalyzeBaseVue,
  props: {

  },
  data() {
    return {
      key: 'anova',
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
  computed: {

  },
  watch: {
  },
  methods: {

  },
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block content
  TODO
</template>

<style scoped lang="scss">

</style>
