<script>
import Heatmap, { heatmapLayouts } from './Heatmap.vue';
import VisTileLarge from './VisTileLarge.vue';
import plotData from './mixins/plotData';
import ToolbarOption from '../toolbar/ToolbarOption.vue';
import MetaboliteFilter from '../toolbar/MetaboliteFilter.vue';
import SampleFilter from '../toolbar/SampleFilter.vue';
import { download } from '../../utils/exporter';
import { colors } from '../../utils/constants';

export default {
  components: {
    Heatmap,
    VisTileLarge,
    ToolbarOption,
    MetaboliteFilter,
    SampleFilter,
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
      column: {
        dendogram: true,
        colorer: this.isSelectedColor,
      },
      row: {
        dendogram: true,
        colorer: this.groupColor,
      },
      dummy: false,
      layout: 'auto',
      layouts: heatmapLayouts,
      metaboliteFilter: null,
      sampleFilter: null,
    };
  },

  computed: {
    values() {
      return this.dataset.validatedMeasurements;
    },
    selectionLookup() {
      return new Set((this.dataset && this.dataset.selectedColumns) || []);
    },
    groupLookup() {
      if (!this.dataset.validatedGroups || !this.dataset.groupLevels) {
        return [];
      }
      const levelLookup = new Map(this.dataset.groupLevels.map(({ name, color }) => [name, color]));
      const groups = this.dataset.validatedGroups;
      return new Map(groups.rowNames.map((row, i) => [row, levelLookup.get(groups.data[i][0])]));
    },
  },
  watch: {
    dataset() {
      this.metaboliteFilter = null;
      this.sampleFilter = null;
    },
  },
  methods: {
    isSelectedColor(column) {
      return this.selectionLookup.has(column) ? colors.selected : colors.notSelected;
    },
    groupColor(row) {
      return this.groupLookup.get(row);
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
    :loading="plot.loading || !dataset.ready || !values || values.data.length === 0")
  template(#controls)
    metabolite-filter(:dataset="dataset", v-model="metaboliteFilter")
    sample-filter(:dataset="dataset", v-model="sampleFilter")

    v-toolbar.darken-3(color="primary", dark, flat, dense)
      v-toolbar-title Dendogram
    v-card.mx-3(flat)
      v-card-actions(:style="{display: 'block'}")
        v-checkbox.my-0(v-model="column.dendogram", label="Metabolite", hide-details)
        v-checkbox.my-0(v-model="row.dendogram", label="Sample", hide-details)

    toolbar-option(title="Layout", :value="layout",
        :options="layouts",
        @change="layout = $event")

  heatmap(ref="heatmap",
      v-if="plot && plot.data && dataset.ready && values",
      :values="values",
      :column-config="column", :row-config="row", :layout="layout",
      :column-clustering="plot.data ? plot.data.column : null",
      :row-clustering="plot.data ? plot.data.row : null")
</template>
