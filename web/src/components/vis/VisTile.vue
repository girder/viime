<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
    },
    loading: {
      default: false,
      type: Boolean,
    },
  },

  data() {
    return {
      scale: 1,
    };
  },

  computed: {
    smallEnough() {
      return this.scale <= 0.5;
    },
    largeEnough() {
      return this.scale >= 4;
    },
    scaleClass() {
      return `scale${Math.round(this.scale * 100)}`;
    },
  },
};
</script>

<template lang="pug">
v-flex(shrink=1, :class="scaleClass")
  .white.rounded.relative
    v-toolbar.primary.darken-3.top-rounded(dark, flat, dense)
      v-toolbar-title {{ title }}
      v-spacer
      v-toolbar-items
        v-btn(@click="scale *= 0.5", :disabled="smallEnough", icon)
          v-icon {{ $vuetify.icons.viewCollapse }}
        v-btn(@click="scale *= 2", :disabled="largeEnough", icon)
          v-icon {{ $vuetify.icons.viewExpand }}
        slot(name="controls")
    v-progress-linear.ma-0.progress(v-if="loading", indeterminate, height=4)
    v-card.bottom-rounded(flat)
      slot(:scale="scale")
</template>

<style scoped lang="scss">
.scale50 {
  grid-column: span 1;
  grid-row: span 1;
}
.scale100 {
  grid-column: span 2;
  grid-row: span 2;
}
.scale200 {
  grid-column: span 4;
  grid-row: span 4;
}
.scale400 {
  grid-column: span 8;
  grid-row: span 8;
}

.relative {
  position: relative;
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

.vis-tile {
  width: 600px;
  max-width: 600px;
  height: 648px;
  max-height: 648px;
}

.progress {
  position: absolute;
}
</style>
