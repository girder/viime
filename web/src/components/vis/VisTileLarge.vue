<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    loading: {
      validator: prop => true,
      required: true,
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
v-layout(v-else, row, fill-height)
  v-navigation-drawer.primary.darken-3.nav-drawer(
      v-if="hasControls", permanent,
      style="width: 200px;min-width: 200px;")
    slot(name="controls")

  v-layout(v-if="loading", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading...

  v-container.grow-overflow.ma-0(grid-list-lg, fluid, v-else)
    slot
</template>
