<script>
import { CHANGE_ANALYSIS_OPTIONS } from '../../store/actions.type';

export default {
  components: {
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    key: 'unknown',
  }),
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    loading() { return this.$store.state.loading; },
    options() { return this.$store.getters.analysisOptions(this.id, this.key); },
    results() { return this.$store.getters.analysisData(this.id, this.key); },
    analysisState() { return this.$store.getters.analysisState(this.id, this.key); },
  },
  watch: {
    ready() {
      if (this.analysisState === 'initial') {
        this.compute();
      }
    },
  },
  created() {
    if (this.analysisState === 'initial') {
      this.compute();
    }
  },
  methods: {
    changeOption(changes) {
      return this.$store.dispatch(CHANGE_ANALYSIS_OPTIONS, {
        dataset_id: this.id,
        key: this.key,
        changes,
      });
    },
    compute() {
      // dummy change to trigger
      return this.changeOption({});
    },
  },
};
</script>

<template lang="pug">
include AnalyzeBase.pug
</template>

<style scoped lang="scss">
</style>
