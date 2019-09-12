<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  extends: AnalyzeBaseVue,
  data() {
    return {
      cards: [
        {
          name: 'Wilcox',
          description: 'TODO fancy description',
          path: 'wilcox'
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
    v-flex(v-for="card in cards", :key="card.path" md6)
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
