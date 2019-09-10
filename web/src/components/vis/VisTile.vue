<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
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
  .white.rounded
    v-toolbar.primary.darken-3.top-rounded(dark, flat, dense)
      v-toolbar-title {{ title }}
      v-spacer
      v-toolbar-items(v-if="hasControls")
        slot(name="controls")

    v-card.rounded(flat)
      slot
</template>

<style scoped lang="scss">
.rounded {
  border-radius: 5px;
}

.top-rounded {
  border-radius: 5px 5px 0 0;
}

.vis-tile {
  width: 600px;
  max-width: 600px;
  height: 648px;
  max-height: 648px;
}
</style>
