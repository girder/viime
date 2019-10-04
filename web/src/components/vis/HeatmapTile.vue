<script>
import Heatmap, { heatmapLayouts } from './Heatmap.vue';
import VisTileLarge from './VisTileLarge.vue';
import plotData from './mixins/plotData';
import ToolbarOption from '../ToolbarOption.vue';

export default {
  components: {
    Heatmap,
    VisTileLarge,
    ToolbarOption,
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
      column: {
        dendogram: true,
      },
      row: {
        dendogram: true,
      },
      layout: 'auto',
      layouts: heatmapLayouts,
    };
  },

  computed: {
    values() {
      return this.dataset.validatedMeasurements;
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Heatmap", expanded,
    :loading="plot.loading || !dataset.ready || !values || values.data.length === 0")
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense)
      v-toolbar-title Dendogram
    v-card.mx-3(flat)
      v-card-actions(:style="{display: 'block'}")
        v-checkbox.my-0(v-model="column.dendogram", label="Metabolite", hide-details)
        v-checkbox.my-0(v-model="row.dendogram", label="Sample", hide-details)
    toolbar-option(title="Layout", :value="layout",
        :options="layouts",
        @change="layout = $event")
  heatmap(
      v-if="plot && dataset.ready && values",
      :values="values",
      :column-config="column", :row-config="row", :layout="layout",
      :column-clustering="plot.data.column",
      :row-clustering="plot.data.row")
</template>
