<script>
import CleanupTable from '../CleanupTable.vue';

export default {
  components: {
    CleanupTable,
  },
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
    };
  },
};
</script>

<template lang="pug">
v-layout(column, fill-height)
  cleanup-table.cleanup-table-flex(:dataset-id="dataset_id")
  v-toolbar(dense, dark)
    v-toolbar-title Table cleanup controls
    v-spacer
    v-toolbar-title
      v-btn(flat, :to="`/transform/${dataset_id}`")
        | Continue
        v-icon.pl-1 {{ $vuetify.icons.arrowRight }}
</template>

<style>
.cleanup-table-flex {
  display: flex;
  flex-basis: 100%;
}
</style>
