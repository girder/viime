<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';
import { CHANGE_ANALYZE_OPTIONS } from '../../store/actions.type';
import {wilcoxon_zero_methods, wilcoxon_alternatives} from '../../utils/constants';

const key = 'wilcoxon';

export default {
  extends: AnalyzeBaseVue,
  components: {
  },
  props: {
    
  },
  data() {
    return {
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
  computed: {
    options() { return this.$store.getters.analyzesOptions(this.id, key); },
    results() { return this.$store.getters.analyzesData(this.id, key); },
  },
  watch: {
  },
  methods: {
    changeOption(changes) {
      return this.$store.dispatch(CHANGE_ANALYZE_OPTIONS, { 
        dataset_id: this.id,
        key,
        changes,
      });
    },
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
          v-radio-group.my-0(:value="options.zero_method",
              hide-details,
              @change="changeOption({zero_method: $event})",)
            v-radio(v-for="m in zero_methods", :label="m.label",
                :value="m.value", :key="`zero${m.value}`")
      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Alternatives
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="options.alternative",
              hide-details,
              @change="changeOption({alternative: $event})",)
            v-radio(v-for="m in alternatives", :label="m.label",
                :value="m.value", :key="`alt${m.value}`")

block content
 div(v-text="results ? JSON.stringify(results) : 'None'")

</template>

<style scoped lang="scss">
</style>
