<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';

const zero_methods = [
  {
    label: '',
    value: 'wilcox'
  },
  {
    label: '',
    value: '“pratt”'
  },
  {
    label: '',
    value: '“zsplit”'
  }
]

export default {
  extends: AnalyzeBaseVue,
  components: {
  },
  props: {
    
  },
  data() {
    return {
      zero_methods
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
      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Zero Methods
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="zero_method",
              hide-details)
            v-radio(v-for="m in zero_methods", :label="m.label",
                :value="m.value", :key="`zero${m.value}`")

block content
 | TODO asdfsd

</template>

<style scoped lang="scss">
</style>
