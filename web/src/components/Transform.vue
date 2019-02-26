<template lang="pug">
v-layout(row, wrap, justify-space-between)
  .pa-2
    v-card.pa-3
      v-card-title
        h3.headline Normalize
      v-card-actions
        v-radio-group(v-model="normalize_current")
          v-radio(v-for="m in normalize_methods", :label="m.label", :value="m.value")
      v-card-title
        h3.meadline Current transformations:
      v-card-text
        v-list
          v-list-tile(v-for="(item, idx) in normalizations", :key="`${idx}${item.transform_type}`")
            v-list-tile-title {{ methodFromValue(item.transform_type).label }}
  .grow.pa-2
    img(:src="`${boxUrl}?type=${normalize_current}`", style="width: 100%")
</template>

<script>
import { mapState } from 'vuex';

import { CSVService } from '../common/api.service';
import { NORMALIZE_TABLE } from '../store/actions.type';


// registry = {
//     'set_value': (set_value, SetValueSchema()),
//     'drop_row': (drop_row, DropRowSchema()),
//     'drop_column': (drop_column, DropColumnSchema()),
//     'normalize': (normalize, NormalizeSchema()),
//     'fill_missing_values_by_constant': (
//         fill_missing_values_by_constant, FillMissingValuesByConstantSchema()),
//     'fill_missing_values_by_mean': (fill_missing_values_by_mean, BaseSchema()),
// }

const normalize_methods = [
  { label: 'None', value: null },
  { label: 'Min Max', value: 'normalize', priority: 10 },
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
      console.log(newval);
      const method = this.methodFromValue(newval);      
      this.$store.dispatch(NORMALIZE_TABLE, { 
        transform_type: newval,
        args: {
          priority: method.priority,
        },
      });
    },
  },
  methods: {
    methodFromValue(value) {
      return normalize_methods.find(m => m.value === value);
    }
  },
  computed: {
    ...mapState(['sourcedata', 'transformdata', 'normalizations']),
    boxUrl() { return CSVService.getChartUrl(this.transformdata.id, 'box'); },
    loadingsUrl() { return CSVService.getChartUrl(this.transformdata.id, 'loadings'); },
  },
}
</script>

<style>

</style>
