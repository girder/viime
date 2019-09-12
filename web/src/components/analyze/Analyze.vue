<script>

export default {
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      cards: [
        {
          name: 'Wilcoxon signed-rank test',
          description: 'The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.',
          path: 'wilcoxon',
        },
      ],
    };
  },
};
</script>

<template lang="pug">
v-layout.analyze-component(row, fill-height)
  v-container.overflow-auto.ma-0(grid-list-lg, fluid)
    v-container.pa-2(fluid)
      v-layout(row)
        v-flex(v-for="card in cards", :key="card.path" md3)
          v-card
            v-card-title(primary-title)
              div
                .headline(v-text="card.name")
                span(v-text="card.description")
            v-card-actions
              v-btn(text,
                @click="$router.push({ path: `/pretreatment/${id}/analyze/${card.path}` })"
              ) Analyze
</template>

<style scoped lang="scss">
</style>
