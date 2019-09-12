<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  extends: AnalyzeBaseVue,
  data() {
    return {
      cards: [
        {
          name: 'Wilcoxon signed-rank test',
          description: `The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.`,
          path: 'wilcoxon'
        }
      ]
    };
  }
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block content
 v-container.pa-2(fluid)
  v-layout(row)
    v-flex(v-for="card in cards", :key="card.path" md3)
      v-card
        v-card-title.fill-height.align-end(v-text="card.name")
        v-card-text(v-text="card.description")
        v-card-actions
          v-btn(text,
            @click="$router.push({ path: `/pretreatment/${dataset.id}/analyze/${card.path}` })"
          ) Analyze
</template>

<style scoped lang="scss">
</style>
