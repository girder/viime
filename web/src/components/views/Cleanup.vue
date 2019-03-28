<script>
import { loadDataset } from '@/utils/mixins';
import CleanupTable from '@/components/CleanupTable.vue';
import SaveStatus from '@/components/SaveStatus.vue';

export default {
  components: {
    CleanupTable,
    SaveStatus,
  },
  mixins: [loadDataset],
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      datasets: this.$store.state.datasets,
    };
  },
};
</script>

<template lang="pug">
v-layout(row, fill-height)
  v-navigation-drawer(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height)
      v-list
        v-list-tile(v-for="(dataset, index) in datasets")
          v-list-tile-title {{ dataset.source.id }}
      v-spacer
      v-btn.accent Next
  v-layout
    cleanup-table.cleanup-table-flex(:dataset-id="dataset_id")
</template>

