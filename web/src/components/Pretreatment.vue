<script>
import { loadDataset } from '@/utils/mixins';

export default {
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
  v-navigation-drawer(permanent, style="width: 200px; min-width: 260px;")
    v-layout(column, fill-height)
      v-list.pt-0
        v-list-group(v-for="(dataset, index) in datasets")
          template(v-slot:activator)
            v-list-tile
              v-list-tile-title {{ dataset.source.id }}
          v-list
            v-list-tile(
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/cleanup` })")
              v-list-tile-title Clean Up Table
            v-list-tile(
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/transform` })")
              v-list-tile-title Transform Table
      v-spacer
      v-btn.accent Next
  v-layout
    router-view(:dataset-id="dataset_id")
</template>
