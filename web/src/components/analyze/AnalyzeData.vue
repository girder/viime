<script>
import Vue from 'vue';
import analyses from '.';

export default Vue.extend({
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      analyses,
    };
  },
});
</script>

<template lang="pug">
v-layout.analyze-component(row, fill-height)
  v-container.grow-overflow.ma-0(grid-list-lg, fluid)
    v-container.pa-2(fluid)
      v-layout(row)
        v-flex(v-for="card in analyses", :key="card.path", md3)
          v-card
            v-card-title(primary-title)
              div
                .headline(v-text="card.name")
                | {{card.description}}
            v-card-actions
              v-btn(text,
                  @click="$router.push({ path: `/pretreatment/${id}/analyze/${card.path}` })")
                | Analyze
</template>
