<script>
import { mapState } from 'vuex';
import { MUTEX_TRANSFORM_TABLE } from '@/store/actions.type';
import {
  normalize_methods,
  scaling_methods,
  transform_methods,
} from '@/utils/constants';
import ScorePlotTile from '@/components/vis/ScorePlotTile.vue';
import ScreePlotTile from '@/components/vis/ScreePlotTile.vue';
import LoadingsPlotTile from '@/components/vis/LoadingsPlotTile.vue';

export default {
  components: {
    LoadingsPlotTile,
    ScorePlotTile,
    ScreePlotTile,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      normalize_methods,
      transform_methods,
      scaling_methods,
    };
  },
  computed: {
    ...mapState(['lastError']),
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    loading() { return this.$store.state.loading; },
    norm() { return this.$store.getters.txType(this.id, 'normalization'); },
    norm_arg() { return this.$store.getters.txType(this.id, 'normalization_argument'); },
    trans() { return this.$store.getters.txType(this.id, 'transformation'); },
    scaling() { return this.$store.getters.txType(this.id, 'scaling'); },
  },
  methods: {
    async transformTable(value, category, argument, methods) {
      /* If there's no argument and there should be, pick the firt from the list */
      const method = methods.find(v => v.value === value);
      if (!method) {
        throw new Error('invalid method');
      }
      let arg = argument;
      if (!arg && method.arg) {
        [arg] = this.getSelectItems(method.arg);
      }
      this.$store.dispatch(MUTEX_TRANSFORM_TABLE, {
        dataset_id: this.id,
        transform_type: value,
        category,
        argument: arg,
      });
    },
    getSelectItems(arg) {
      const opts = arg.split('.');
      const order = opts[0]; // row or column
      const _type = opts[1]; // sample, metadata, group, metabolite, etc.
      const value = opts[2]; // name, header, index, etc.
      return this.dataset[order]
        .data.filter(v => v[`${order}_type`] === _type)
        .map(v => v[`${order}_${value}`]);
    },
  },
};
</script>

<template lang="pug">
v-layout.transform-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
        v-toolbar-title Normalize
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="norm",
              @change="transformTable($event, 'normalization', null, normalize_methods)",
              hide-details)
            .radio-container.my-1(v-for="m in normalize_methods", :key="m.value",
                v-if="!m.arg || getSelectItems(m.arg).length > 0")
              v-radio(:label="m.label", :value="m.value")
              v-select.mb-3(solo, dense, hide-details, v-if="m.arg && m.value === norm",
                  :items="getSelectItems(m.arg)",
                  @input="transformTable(norm, 'normalization', $event, normalize_methods)",
                  :value="norm_arg || getSelectItems(m.arg)[0]")

      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Transform
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="trans",
              @change="transformTable($event, 'transformation', null, transform_methods)",
              hide-details)
            v-radio(v-for="m in transform_methods", :label="m.label",
                :value="m.value", :key="`trans${m.value}`")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Scale
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="scaling",
              @change="transformTable($event, 'scaling', null, scaling_methods)",
              hide-details)
            v-radio(v-for="m in scaling_methods", :label="m.label",
                :value="m.value", :key="`scale${m.value}`")

  v-layout(v-if="!dataset || !ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
  v-layout(column, v-else-if="ready && valid")
    v-container.grow-overflow.ma-0(grid-list-lg, fluid)
      v-layout(row, wrap)
        score-plot-tile(
            :width="600",
            :height="600",
            :columns="dataset._source.columns"
            :id="id")
        loadings-plot-tile(
            :width="600",
            :height="600",
            :id="id")
        scree-plot-tile(
            :width="600",
            :height="600",
            :id="id")
  v-container(v-else-if="ready", fill-height)
    v-layout(column)
      .display-2 Error: Cannot show transform table
      a.headline(:href="`#/pretreatment/${dataset.id}/cleanup`") Correct validation error(s)
</template>

<style scoped lang="scss">
.transform-component {
  background: #eee;
}
</style>
