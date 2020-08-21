<script>
import { downloadSVG } from '../../utils/exporter';
import { analysisTable } from '@/components/vis/analyses';
import RenderJsx from '@/utils/RenderJsx';

export default {
  components: {
    RenderJsx,
  },

  props: {
    title: {
      type: String,
      required: true,
    },
    analysisPath: {
      type: String,
      default: '',
    },
    loading: {
      type: Boolean,
      default: false,
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

    helpText() {
      if (this.analysisPath) {
        return analysisTable[this.analysisPath].description;
      }
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
      style="width: 215px;min-width: 215px;",
      touchless, disable-resize-watcher, stateless)
    slot(name="controls")

    div(v-if="download")
      v-btn(flat, dark, block, @click="downloadImage")
        v-icon.mr-2 {{ $vuetify.icons.save }}
        | Download PNG

    v-menu(v-if="helpText", offset-y)
      template(v-slot:activator="{ on }")
        v-btn(flat, dark, block, v-on="on")
          v-icon.mr-2 {{ $vuetify.icons.help }}
          | What is this?
      v-card(max-width=300)
        render-jsx(:f="helpText")

  v-layout(v-if="loading", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading...

  v-layout(column, v-else)
    v-container.grow-overflow.ma-0.mainContainer(grid-list-lg, fluid)
      slot
</template>

<style lang="scss" scoped>
.mainContainer {
  position: relative;
}
</style>
