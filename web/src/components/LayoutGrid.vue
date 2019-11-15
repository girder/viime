<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

@Component
export default class LayoutGrid extends Vue {
  @Prop({
    required: true,
  })
  readonly cellSize!: number;

  gridHint = 4;

  get gridStyle() {
    return {
      gridTemplateColumns: `repeat(${this.gridHint}, ${this.cellSize}px)`,
      gridAutoColumns: `${this.cellSize}px`,
      gridAutoRows: `${this.cellSize}px`,
    };
  }

  mounted() {
    const available = this.$el.getBoundingClientRect().width;
    // compute the number of horizontal cells based on the container width
    this.gridHint = Math.floor(available / this.cellSize);
  }
}
</script>

<template lang="pug">
.gridlayout(:style="gridStyle")
  slot
</template>

<style scoped lang="scss">
.gridlayout {
  display: grid;
  grid-gap: 0.5em;
}
</style>
