<script>
import { IMPORT_SAMPLE, IMPORT_SAMPLE_GROUP } from '../store/actions.type';
import { SampleService } from '../common/api.service';


export default {
  data() {
    return {
      loading: true,
      samples: [],
    };
  },
  computed: {

  },
  async created() {
    this.loading = true;
    this.samples = (await SampleService.list()).data;
    this.loading = false;
  },
  methods: {
    async importGroup(group, evt) {
      evt.preventDefault();
      evt.stopPropagation();
      await this.$store.dispatch(IMPORT_SAMPLE_GROUP, { group });
      this.$emit('close');
    },
    async importSample(sampleId, evt) {
      evt.preventDefault();
      evt.stopPropagation();
      await this.$store.dispatch(IMPORT_SAMPLE, { sampleId });
      this.$emit('close');
    },
  },
};
</script>

<template lang="pug">
.root
  .text-xs-center(v-if="loading")
    v-progress-circular(indeterminate, color="primary")
  v-alert(:value="!loading && samples.length === 0", type="info")
    | No Sample Data Sources available
  v-expansion-panel(v-if="!loading && samples.length > 0", :value="0")
    v-expansion-panel-content.group(v-for="group,index in samples", :key="group.name",
        :readonly="samples.length === 1")
      template(#header)
        span {{ group.name }}
        v-btn.import(color="primary", @click="importGroup(group.name, $event)") Import All

      v-card
        v-card-text
          | {{ group.description || 'no description available' }}

      v-expansion-panel
        v-expansion-panel-content.file(v-for="file in group.files", :key="file.id")
          template(#header)
            span {{ file.name }}
            v-btn.import(color="primary", @click="importSample(file.id, $event)") Import

          v-card
            v-card-text
              | {{ file.description || 'no description available' }}
</template>

<style scoped lang="scss">
.import {
  flex: 0 0 auto;
}
</style>
