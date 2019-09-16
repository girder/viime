<script>
import Vue from 'vue';

export default Vue.extend({
  props: {
    id: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    toolbarHidden: {
      type: Boolean,
    },
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    loading() { return this.$store.state.loading; },
    analysisState() { return this.$store.getters.analysisState(this.id, this.name); },
  },
});
</script>

<template lang="pug">
v-layout(row, fill-height)
  v-navigation-drawer.primary.darken-3(v-if="dataset && ready && !toolbarHidden",
      permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height)
      slot(name="toolbar")

  v-layout(v-if="!dataset || !ready", :key="layout", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set

  v-layout(v-else-if="analysisState === 'computing'", :key="layout", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Computing...

  v-container.grow-overflow.ma-0(grid-list-lg, fluid,
      v-else-if="dataset && ready && valid && analysisState === 'ready'")
    slot
</template>
