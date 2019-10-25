<script>
import { downloadSVG } from '../../utils/exporter';

export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
    download: {
      default: false,
      type: Boolean,
    },
    downloadImpl: {
      default: null,
      type: Function,
    },
  },

  computed: {
    hasControls() {
      return !!this.$slots.controls || !!this.$scopedSlots.controls;
    },
  },

  methods: {
    downloadImage() {
      if (this.downloadImpl) {
        this.downloadImpl(this.$el);
        return;
      }
      const svg = this.$el.querySelector('svg');
      if (svg) {
        downloadSVG(svg, this.title);
      }
    },
  },
};
</script>

<template lang="pug">
v-layout(v-else, row, fill-height)
  v-navigation-drawer.primary.darken-3.nav-drawer(
      v-if="hasControls", permanent,
      style="width: 200px;min-width: 200px;")
    slot(name="controls")

    div(v-if="download")
      v-btn(flat, dark, block, @click="downloadImage")
        v-icon.mr-2 {{ $vuetify.icons.save }}
        | Download PNG

  v-layout(v-if="loading", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading...

  v-container.grow-overflow.ma-0.mainContainer(grid-list-lg, fluid, v-else)
    slot
</template>

<style lang="scss" scoped>
.mainContainer {
  position: relative;
}
</style>
