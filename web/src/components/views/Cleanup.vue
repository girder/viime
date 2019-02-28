<script>
import { mapState } from 'vuex';
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
  computed: {
    ...mapState(['datasets']),
    meta() {
      return {
        width: this.datasets[this.dataset_id].sourcerows.data[0].length,
        height: this.datasets[this.dataset_id].sourcerows.data.length,
      }
    },
  }
};
</script>

<template lang="pug">
v-layout(column, fill-height)
  cleanup-table.cleanup-table-flex.py-2(
      :rows="datasets[dataset_id].sourcerows.data",
      :metadata="meta")
  v-toolbar(dense, dark)
    v-toolbar-title Table cleanup controls
    v-spacer
    v-toolbar-title2
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
