<template lang="pug">
v-layout(row, wrap)
  v-radio-group(v-model="normalize_current")
    v-radio(v-for="m in normalize_methods", :label="m.label", :value="m.value")
  div.grow
    img(:src="scoresUrl", :key="normalize_current")
  div
    p(v-for="col in sourcedata.columns") {{ col.name }}
</template>

<script>
import { mapState } from 'vuex';

import { CSVService } from '../common/api.service';
import { NORMALIZE_TABLE } from '../store/actions.type';

const normalize_methods = [
  { label: 'None', value: 'none' },
  { label: 'Min Max', value: 'minmax' },
];

export default {
  data() {
    return {
      normalize_current: normalize_methods[0].value,
      normalize_methods,
    };
  },
  watch: {
    normalize_current(newval) {
      this.$store.dispatch(NORMALIZE_TABLE, { method: newval });
    },
  },
  computed: {
    ...mapState(['sourcedata', 'transformdata']),
    scoresUrl() { return CSVService.getChartUrl(this.transformdata.id, 'scores'); },
    loadingsUrl() { return CSVService.getChartUrl(this.transformdata.id, 'loadings'); },
  },
}
</script>

<style>

</style>
