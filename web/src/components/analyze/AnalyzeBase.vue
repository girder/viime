<script>
export default {
  components: {
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    loading() { return this.$store.state.loading; },
  },
  watch: {
  },
  methods: {

  },
};
</script>

<template lang="pug">
include AnalyzeBase.pug
</template>

<style scoped lang="scss">
</style>
