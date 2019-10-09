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
        colorer: this.isSelectedColor,
      },
      row: {
        dendogram: true,
        colorer: this.groupColor,
      },
      dummy: false,
      layout: 'auto',
      layouts: heatmapLayouts,
    };
  },

  computed: {
    values() {
      return this.dataset.validatedMeasurements;
    },
    countSelected() {
      return !this.dataset ? 0 : (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.dataset || !this.values) {
        return 0;
      }
      return this.values.columnNames.length - this.countSelected;
    },
    showSetting() {
      return this.plot.args.columns;
    },
    showSelected: {
      get() {
        return !this.showSetting || this.showSetting === 'selected';
      },
      set(value) {
        let columns = '';
        if (value) {
          columns = this.showSetting === 'not-selected' ? null : 'selected';
        } else {
          columns = 'not-selected'; // always show at least one
        }
        this.changePlotArgs({ columns });
      },
    },
    showNotSelected: {
      get() {
        return !this.showSetting || this.showSetting === 'not-selected';
      },
      set(value) {
        let columns = '';
        if (value) {
          columns = this.showSetting === 'selected' ? null : 'not-selected';
        } else {
          columns = 'selected';
        }
        this.changePlotArgs({ columns });
      },
    },
    selectionLookup() {
      return new Set((this.dataset && this.dataset.selectedColumns) || []);
    },
    groupLookup() {
      if (!this.dataset.validatedGroups || !this.dataset.groupLevels) {
        return [];
      }
      const levelLookup = new Map(this.dataset.groupLevels.map(({ name, color }) => [name, color]));
      return this.dataset.validatedGroups.data.map(row => levelLookup.get(row[0]));
    },
  },
  methods: {
    isSelectedColor(index) {
      const column = this.values.columnNames[index];
      return this.selectionLookup.has(column) ? '#ffa500' : '#4682b4';
    },
    groupColor(index) {
      return this.groupLookup[index];
    },
  },
};

</script>

<template lang="pug">
vis-tile-large(v-if="plot", title="Heatmap", expanded,
    :loading="plot.loading || !dataset.ready || !values || values.data.length === 0")
  template(#controls)
    v-toolbar.darken-3(color="primary", dark, flat, dense)
      v-toolbar-title Metabolite Filter
    v-card.mx-3(flat)
      v-card-actions(:style="{display: 'block'}")
        v-checkbox.my-0(v-model="showSelected",
            :label="`Selected (${countSelected})`", hide-details, color="#ffa500")
        v-checkbox.my-0(v-model="showNotSelected",
            :label="`Not Selected (${countNotSelected})`", hide-details, color="#4682b4")
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
      v-if="plot && plot.data && dataset.ready && values",
      :values="values",
      :column-config="column", :row-config="row", :layout="layout",
      :column-clustering="plot.data.column",
      :row-clustering="plot.data.row")
</template>
