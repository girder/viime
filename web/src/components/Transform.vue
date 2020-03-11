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
import BoxPlotTile from '@/components/vis/BoxPlotTile.vue';
import LayoutGrid from './LayoutGrid.vue';
import ToolbarOption from './toolbar/ToolbarOption.vue';
import { CSVService } from '../common/api.service';

export default {
  components: {
    LoadingsPlotTile,
    ScorePlotTile,
    ScreePlotTile,
    BoxPlotTile,
    LayoutGrid,
    ToolbarOption,
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
      visiblePlots: {
        score: true,
        scree: true,
        loadings: true,
        boxplot: true,
      },
      cellSize: 300,
    };
  },
  computed: {
    ...mapState(['lastError']),
    dataset() { return this.$store.getters.dataset(this.id); },
    ready() { return this.$store.getters.ready(this.id); },
    valid() { return this.$store.getters.valid(this.id); },
    norm() { return this.$store.getters.txType(this.id, 'normalization'); },
    norm_arg() { return this.$store.getters.txType(this.id, 'normalization_argument'); },
    trans() { return this.$store.getters.txType(this.id, 'transformation'); },
    scaling() { return this.$store.getters.txType(this.id, 'scaling'); },
    downloadLink() {
      return CSVService.validatedDownloadUrl(this.id);
    },
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
        // take first one
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
      return arg(this.dataset);
    },
  },
};
</script>

<template lang="pug">
v-layout.transform-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;",
      touchless, disable-resize-watcher, stateless)
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

      toolbar-option(title="Transform", :value="trans",
          @change="transformTable($event, 'transformation', null, transform_methods)",
          :options="transform_methods")

      toolbar-option(title="Scale", :value="scaling",
          @change="transformTable($event, 'scaling', null, scaling_methods)",
          :options="scaling_methods")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Plots
      v-card.mx-3(flat)
        v-card-actions.checkboxlist
          v-checkbox.my-0(v-model="visiblePlots.score", label="PCA Score Plot", hide-details)
          v-checkbox.my-0(v-model="visiblePlots.loadings", label="PCA Loadings Plot", hide-details)
          v-checkbox.my-0(v-model="visiblePlots.scree", label="PCA Scree Plot", hide-details)
          v-checkbox.my-0(v-model="visiblePlots.boxplot", label="Boxplot Plot", hide-details)

      v-btn.mx-3(flat, dark, :href="downloadLink", :disabled="!valid") Download CSV

  v-layout(v-if="!dataset || !ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set
  v-layout(column, v-else-if="ready && valid")
    v-container.grow-overflow.ma-0(grid-list-lg, fluid)
      layout-grid(:cell-size="cellSize")
        score-plot-tile(
            v-if="visiblePlots.score",
            :id="id")
        loadings-plot-tile(
            v-if="visiblePlots.loadings",
            :id="id")
        scree-plot-tile(
            v-if="visiblePlots.scree",
            :id="id")
        box-plot-tile(
            v-if="visiblePlots.boxplot",
            :id="id")
  v-container(v-else-if="ready", fill-height)
    v-layout(column)
      .display-2 Error: Cannot show transform table
      a.headline(:to="{ name: 'Clean Up Table', params: { id: dataset.id }}")
        | Correct validation error(s)
</template>

<style scoped lang="scss">
.transform-component {
  background: #eee;
}

.checkboxlist {
  display: block;
}

</style>
