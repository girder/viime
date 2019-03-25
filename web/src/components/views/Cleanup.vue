<script>
import { loadDataset } from '@/utils/mixins';
import CleanupTable from '@/components/CleanupTable.vue';
import HeaderFooterContainer from '@/components/containers/HeaderFooter.vue';
import SaveStatus from '@/components/SaveStatus.vue';
import Stepper from '@/components/stepper/Stepper.vue';

export default {
  components: {
    CleanupTable,
    HeaderFooterContainer,
    SaveStatus,
    Stepper,
  },
  mixins: [loadDataset],
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      stepperCollapsed: true,
      stepperModel: 1,
    };
  },
};
</script>

<template lang="pug">
header-footer-container

  template(#header)
    stepper(v-model="stepperModel", :collapsed.sync="stepperCollapsed")

  cleanup-table.cleanup-table-flex(:dataset-id="dataset_id")

  template(#footer)
    v-toolbar.footer(flat, dense)
      v-btn(depressed, color="accent", :to="`/select`")
        v-icon.pr-1 {{ $vuetify.icons.arrowLeft }}
        | Go Back
      v-spacer
      save-status
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
