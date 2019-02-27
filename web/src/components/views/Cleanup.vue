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
    v-toolbar-title Table control footer
    v-spacer
    v-toolbar-footer
      v-icon {{ $vuetify.icons.more }}
</template>

<style>
.cleanup-table-flex {
  display: flex;
  flex-basis: 100%;
}
</style>
