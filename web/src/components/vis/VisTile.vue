<script>
import { downloadSVG } from '../../utils/exporter';
import HelpDialog from '../toolbar/HelpDialog.vue';

export default {
  components: {
    HelpDialog,
  },
  props: {
    title: {
      type: String,
      default: '',
    },
    loading: {
      default: false,
      type: Boolean,
    },
    svgDownload: {
      default: false,
      type: Boolean,
    },
  },

  data() {
    return {
      showHelp: false,
    };
  },

  methods: {
    hasHelp() {
      return this.$slots.help != null || this.$scopedSlots.help != null;
    },
    downloadSVG() {
      const svg = this.$el.querySelector('svg');
      if (svg) {
        downloadSVG(svg, this.title);
      }
    },
  },
};
</script>

<template lang="pug">
v-flex.white.rounded.main(shrink=1)
  v-toolbar.primary.darken-3.top-rounded(dark, flat, dense)
    v-toolbar-title {{ title }}
    v-toolbar-items(v-if="hasHelp()")
      help-dialog(:title="title")
        slot(name="help")
    v-spacer
    v-toolbar-items
      v-btn(v-if="svgDownload", @click="downloadSVG", icon)
        v-icon {{ $vuetify.icons.save }}
      slot(name="controls")
  v-progress-linear.ma-0.progress(v-if="loading", indeterminate, height=4)
  v-card.bottom-rounded.content(flat)
    slot
</template>

<style scoped lang="scss">
.main {
  position: relative;
  display: flex;
  flex-direction: column;
  grid-column: span 2;
  grid-row: span 2;
}
.rounded {
  border-radius: 5px;
}

.top-rounded {
  border-radius: 5px 5px 0 0;
}

.bottom-rounded {
  border-radius: 0 0 5px 5px;
}

.progress {
  position: absolute;
}
</style>

<style scoped>

.content {
  flex: 1 1 0;
  display: flex;
  flex-direction: column
}

.content >>> > * {
  flex: 1 1 0;
  overflow: hidden;
}
</style>
