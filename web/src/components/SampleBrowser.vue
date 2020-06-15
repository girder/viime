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
  v-expansion-panel.sample-panels.elevation-0(v-if="!loading && samples.length > 0", :value="0")
    v-expansion-panel-content.group(v-for="group,index in samples", :key="group.name",
        :readonly="samples.length === 1")
      template(#header)
        span {{ group.name }}
        v-btn.import(color="primary", @click="importGroup(group.name, $event)") Import All

      v-card(color="transparent")
        v-card-text.pa-4
          | {{ group.description || 'no description available' }}

      v-expansion-panel.pb-4.px-4.elevation-0
        v-expansion-panel-content.file(v-for="file in group.files", :key="file.id")
          template(#header)
            span {{ file.name }}
            v-btn.import(color="primary", @click="importSample(file.id, $event)", flat) Import

          v-card
            v-card-text
              | {{ file.description || 'no description available' }}
</template>

<style scoped lang="scss">
.import {
  flex: 0 0 auto;
}

.sample-panels {
  border-bottom: 1px solid var(--v-primary-lighten4);
  border-top: 1px solid var(--v-primary-lighten4);

  /deep/ .v-expansion-panel__body {
    background: var(--v-primary-lighten5);
    box-shadow: inset 0px 0px 4px rgba(0, 0, 0, .25);
  }
}
</style>
