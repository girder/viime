<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import analyses from './vis/analyses';
import RenderJsx from '../utils/RenderJsx';

@Component({
  components: {
    RenderJsx,
  },
})
export default class AnalyzeData extends Vue {
  @Prop({
    required: true,
  })
  readonly id!: string;

  readonly analyses = analyses;
}
</script>

<template lang="pug">
v-layout.analyze-component(row, fill-height)
  v-container.grow-overflow.ma-0(grid-list-lg, fluid)
    v-container.pa-2(fluid)
      v-layout(row, wrap)
        v-flex(v-for="card in analyses", :key="card.path", md3)
          v-card.card
            v-card-title(primary-title)
              .headline {{ card.name }}
            .desc
              render-jsx(:f="card.description")
            v-card-actions
              v-btn(text,
                  @click="$router.push({ name: card.shortName, params: { id } })")
                | Analyze
</template>

<style lang="scss" scoped>
.card {
  display: flex;
  flex-direction: column;
  height: 100%;

  > .desc {
    flex: 1 1 0;
    padding: 0 1em;
  }

  > .v-card__actions {
    flex-direction: column;
    align-items: flex-end;
  }
}
</style>
