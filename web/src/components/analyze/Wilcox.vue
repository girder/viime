<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';

export default {
  extends: AnalyzeBaseVue,
  components: {
  },
  props: {
    
  },
  data() {
    return {
    };
  },
  computed: {
    
  },
  watch: {
  },
  methods: {

  },
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block toolbar
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
        | Option 1

block content
 | TODO asdfsd

</template>

<style scoped lang="scss">
</style>
