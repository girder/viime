<script>
import { MUTEX_TRANSFORM_TABLE, LOAD_PLOT } from '@/store/actions.type';

export default {
  components: {
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    loading() { return this.$store.state.loading; },
  },
  watch: {
  },
  methods: {

  },
};
</script>

<template lang="pug">
v-layout.analyze-wilcox-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
        v-toolbar-title Options
      v-card.mx-3(flat)
        v-card-actions
          span TODO
  v-layout(v-if="!dataset || !ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
  v-container.overflow-auto.ma-0(grid-list-lg, fluid, v-else-if="ready && valid")
    span TODO
  v-container.overflow-auto(v-else-if="ready", fill-height)
    v-layout(column)
      .display-2 Error: Cannot analyze data
      a.headline(:href="`#/pretreatment/${dataset.id}/cleanup`") Correct validation error(s)
</template>

<style scoped lang="scss">
.analyze-wilcox-component {
  background: #eee;
}
</style>
