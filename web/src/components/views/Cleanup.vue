<script>
import { loadDataset } from '@/utils/mixins';
import CleanupTable from '@/components/CleanupTable.vue';
import FooterContainer from '@/components/containers/FooterContainer.vue';

export default {
  components: {
    CleanupTable,
    FooterContainer,
  },
  mixins: [loadDataset],
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
    };
  },
};
</script>

<template lang="pug">
footer-container

  cleanup-table.cleanup-table-flex(:dataset-id="dataset_id")

  template(#footer)
    v-toolbar(flat)
      v-btn(depressed, color="accent", :to="`/select`")
        v-icon.pr-1 {{ $vuetify.icons.arrowLeft }}
        | Go Back
      v-spacer
      v-btn(depressed, color="accent", :to="`/transform/${dataset_id}`")
        | Continue
        v-icon.pl-1 {{ $vuetify.icons.arrowRight }}
</template>

<style>
.cleanup-table-flex {
  display: flex;
  flex-basis: 100%;
}
</style>
