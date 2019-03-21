<script>
export default {
  computed: {
    loading() { return this.$store.state.loading; },
  },
}
</script>

<template lang="pug">
.save-status
  v-tooltip(top)
    template(v-slot:activator="{ on }")
      div(v-if="loading")
        span(v-on="on") Saving...
      div(v-else)
        span(v-on="on") All changes saved.
    span Changes you make on this page are automatically saved.
</template>

<style scoped>
.save-status span {
  text-decoration: underline;
}
</style>
