<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
    },
    loading: {
      type: Boolean,
      default: false,
    },
    expanded: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    hasControls() {
      return !!this.$slots.controls;
    },
  },
};
</script>

<template lang="pug">
v-flex(shrink=1)
  
  .white.rounded.relative(v-if="!expanded")
    v-toolbar.primary.darken-3.top-rounded(dark, flat, dense)
      v-toolbar-title {{ title }}
      v-spacer
      v-toolbar-items(v-if="hasControls")
        slot(name="controls")
    v-progress-linear.ma-0.progress(v-if="loading", indeterminate, height=4)
    v-card.bottom-rounded(flat)
      slot
  
  v-layout(v-else, row, fill-height)
    v-navigation-drawer.primary.darken-3.nav-drawer(
        permanent,
        style="width: 200px;min-width: 200px;")
      slot(name="controls")
    v-layout(v-if="loading", justify-center, align-center)
      v-progress-circular(indeterminate, size="100", width="5")
      h4.display-1.pa-3 Loading
    slot(v-else)
</template>

<style scoped lang="scss">
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
