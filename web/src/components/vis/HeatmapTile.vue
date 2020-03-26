<script>
import Heatmap, { heatmapLayouts } from './Heatmap.vue';
import VisTileLarge from './VisTileLarge.vue';
import plotData from './mixins/plotData';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import SampleFilter from '../toolbar/SampleFilter.vue';
import MetaboliteColorer from '../toolbar/MetaboliteColorer.vue';
import SampleColorer from '../toolbar/SampleColorer.vue';
import { download } from '../../utils/exporter';
import { colors } from '../../utils/constants';

export default {
  components: {
    Heatmap,
    VisTileLarge,
    ToolbarOption,
    MetaboliteFilter,
    SampleFilter,
    MetaboliteColorer,
    SampleColorer,
  },

  mixins: [plotData('heatmap')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      colors,
      cluster: true,
      row: {
        dendrogram: true,
        colorer: this.columnColor,
      },
      column: {
        dendrogram: true,
        colorer: this.rowColor,
      },
      dummy: false,
      layout: 'auto',
      layouts: heatmapLayouts,
      metaboliteFilter: null,
      sampleFilter: null,
      metaboliteColor: null,
      sampleColor: null,
    };
  },

  computed: {
    values() {
      if (!this.plot.data) {
        return [];
      }
      // TODO swap
      return this.plot.data ? this.plot.data.values : [];
    },
  },
  watch: {
    cluster() {
      if (!this.cluster) {
        this.row.dendrogram = false;
        this.column.dendrogram = false;
      }
    },
    metaboliteFilter(newValue) {
      if (newValue && newValue.option) {
        this.changePlotArgs({
          column: newValue.option,
          column_filter: newValue.filter.join(','),
        });
      } else {
        this.changePlotArgs({
          column: null,
          column_filter: null,
        });
      }
    },
    sampleFilter(newValue) {
      if (newValue && newValue.option) {
        this.changePlotArgs({
          row: newValue.option,
          row_filter: newValue.filter.join(','),
        });
      } else {
        this.changePlotArgs({
          row: null,
          row_filter: null,
        });
      }
    },
  },
  methods: {
    columnColor(column) {
      return this.metaboliteColor ? this.metaboliteColor.apply(column) : null;
    },
    rowColor(row) {
      return this.sampleColor ? this.sampleColor.apply(row) : null;
    },
    async download() {
      if (!this.$refs.heatmap) {
        return;
      }
      const url = await this.$refs.heatmap.generateImage();
      download(url, 'Heatmap.png');
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Heatmap", expanded, download, :download-impl="download",
    :loading="plot.loading || !dataset.ready || !values || values.length === 0")
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter")
    sample-filter(:dataset="dataset", v-model="sampleFilter")

    metabolite-colorer(:dataset="dataset", v-model="metaboliteColor")
    sample-colorer(:dataset="dataset", v-model="sampleColor")

    v-toolbar.darken-3(color="primary", dark, flat, dense)
      v-toolbar-title.switch-title Dendrogram
        v-switch.switch(v-model="cluster", hide-details)
    v-card.mx-3(flat)
      v-card-actions(:style="{display: 'block'}")
        v-checkbox.my-0(
            v-model="row.dendrogram",
            label="Metabolite",
            hide-details,
            :disabled="!cluster")
        v-checkbox.my-0(
            v-model="column.dendrogram",
            label="Sample",
            hide-details,
            :disabled="!cluster")
    toolbar-option(title="Layout", :value="layout",
        :options="layouts",
        @change="layout = $event")

  heatmap(ref="heatmap",
      v-if="plot && plot.data && dataset.ready && values",
      :cluster="cluster",
      :values="values", transposed,
      :column-config="column", :row-config="row", :layout="layout",
      :row-clustering="plot.data ? plot.data.column : null",
      :column-clustering="plot.data ? plot.data.row : null")
</template>

<style lang="scss" scoped>
.switch-title {
  align-items: center;
  display: flex;
  justify-content: space-between;
  overflow: visible;
  width: 100%;
  .switch {
    flex-grow: 0;
    margin-right: -10px;
  }
}
</style>
