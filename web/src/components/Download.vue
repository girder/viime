<script>
import DataTable from './DataTable.vue';
import ToolbarOption from './ToolbarOption.vue';
import { textColor } from '../utils';
import { downloadCSV, download } from '../utils/exporter';
import { CSVService } from '../common/api.service';


export default {
  components: {
    DataTable,
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
      transpose: false,
      showSelected: true,
      showNotSelected: true,
      hiddenGroups: [],
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    dataframe() { return this.dataset.validatedMeasurements; },
    ready() { return this.$store.getters.ready(this.id); },
    loading() { return this.$store.state.loading; },

    selectionLookup() {
      return new Set((this.dataset && this.dataset.selectedColumns) || []);
    },
    groupLookup() {
      if (!this.dataset.validatedGroups || !this.dataset.groupLevels) {
        return [];
      }
      const levelLookup = new Map(this.dataset.groupLevels.map(level => [level.name, level]));
      const groups = this.dataset.validatedGroups;
      return new Map(groups.rowNames.map((row, i) => [row, levelLookup.get(groups.data[i][0])]));
    },

    groupLevels() {
      if (!this.dataset || !this.dataset.validatedGroups) {
        return [];
      }
      const groups = this.dataset.validatedGroups.data;
      return this.dataset.groupLevels.map(level => ({
        ...level,
        count: groups.reduce((acc, row) => acc + (row[0] === level.name ? 1 : 0), 0),
      }));
    },

    countSelected() {
      return !this.dataset ? 0 : (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.dataset || !this.dataframe) {
        return 0;
      }
      return this.dataframe.columnNames.length - this.countSelected;
    },
    filteredColumnNames() {
      if (!this.dataset || !this.dataframe) {
        return [];
      }
      const base = this.dataframe.columnNames.map((text, i) => ({ text, i }));
      if (this.showSelected && this.showNotSelected) {
        return base;
      }
      return base.filter(({ text }) => (
        this.selectionLookup.has(text) ? this.showSelected : this.showNotSelected
      ));
    },
    filteredRowNames() {
      if (!this.dataset || !this.dataframe) {
        return [];
      }
      const base = this.dataframe.rowNames.map((text, i) => ({ text, i }));
      const hidden = new Set(this.hiddenGroups);
      if (hidden.size === 0) {
        return base;
      }
      return base.filter(({ text }) => (
        !this.groupLookup.has(text) || !hidden.has(this.groupLookup.get(text).name)
      ));
    },
    extraRowHeaders() {
      let extras = [];

      if (!this.transpose && this.dataset.validatedMeasurementsMetaData) {
        extras = this.dataset.validatedMeasurementsMetaData.rowNames;
      } else if (this.transpose && this.dataset.validatedSampleMetaData) {
        extras = this.dataset.validatedSampleMetaData.columnNames;
      }

      return extras.map(text => ({
        text,
        clazz: ['type-metadata'],
      }));
    },
    rowHeaders() {
      if (this.transpose) {
        return [...this.extraRowHeaders, ...this.filteredColumnNames.map(({ text }) => ({
          text,
          style: this.getStyle(this.isSelectedColor(text)),
        }))];
      }

      return [...this.extraRowHeaders, ...this.filteredRowNames.map(({ text }) => ({
        text,
        style: this.getStyle(this.groupColor(text)),
      }))];
    },
    extraColumns() {
      const { validatedSampleMetaData, validatedMeasurementsMetaData } = this.dataset;
      const extras = this.extraRowHeaders.map(() => '');

      if (!this.transpose && validatedSampleMetaData) {
        return validatedSampleMetaData.columnNames.map((text, i) => ({
          index: i,
          header: { text, clazz: ['type-metadata'] },
          values: [...extras, ...validatedSampleMetaData.data.map(row => row[i])],
        }));
      }

      if (this.transpose && validatedMeasurementsMetaData) {
        return validatedMeasurementsMetaData.rowNames.map((text, i) => ({
          index: i,
          header: { text, clazz: ['type-metadata'] },
          values: [...extras, ...validatedMeasurementsMetaData.data[i]],
        }));
      }
      return [];
    },
    columns() {
      if (!this.dataframe) {
        return [];
      }
      const { data } = this.dataframe;
      const f = v => (typeof v === 'number' ? v.toFixed(3) : v);

      const { validatedSampleMetaData, validatedMeasurementsMetaData } = this.dataset;
      const extras = this.extraRowHeaders;

      if (this.transpose) {
        return [...this.extraColumns, ...this.filteredRowNames.map(({ text, i }) => ({
          index: i + this.extraColumns.length,
          header: { text, style: this.getStyle(this.groupColor(text)) },
          values: [
            ...extras.map((_, j) => validatedSampleMetaData.data[i][j]),
            ...this.filteredColumnNames.map(({ i: j }) => f(data[i][j])),
          ],
        }))];
      }

      return [...this.extraColumns, ...this.filteredColumnNames.map(({ text, i: j }) => ({
        index: j + this.extraColumns.length,
        header: { text, style: this.getStyle(this.isSelectedColor(text)) },
        values: [
          ...extras.map((_, i) => validatedMeasurementsMetaData.data[i][j]),
          ...this.filteredRowNames.map(({ i }) => f(data[i][j])),
        ],
      }))];
    },
    corner() {
      return `${this.rowHeaders.length} x ${this.columns.length}`;
    },
  },
  methods: {
    cellClasses(rowIndex, columnIndex) {
      if (rowIndex < this.extraRowHeaders.length || columnIndex < this.extraColumns.length) {
        return ['type-metadata'];
      }
      return ['type-sample'];
    },
    isSelectedColor(column) {
      return this.selectionLookup.has(column) ? '#ffa500' : '#4682b4';
    },
    groupColor(row) {
      return (this.groupLookup.get(row) || { color: null }).color;
    },
    getStyle(color) {
      return {
        background: color,
        color: textColor(color),
      };
    },
    setLevelVisible(level, value) {
      if (value) {
        this.hiddenGroups.splice(this.hiddenGroups.indexOf(level.name), 1);
      } else {
        this.hiddenGroups.push(level.name);
      }
    },

    downloadTable() {
      const args = {
        transpose: this.transpose,
      };
      if (this.hiddenGroups.length > 0) {
        args.rows = this.dataset.groupLevels.filter(g => !this.hiddenGroups.includes(g.name)).map(d => d.name).join(',');
      }
      if (!this.showSelected && this.showNotSelected) {
        args.columns = 'not-selected';
      } else if (this.showSelected && !this.showNotSelected) {
        args.columns = 'selected';
      } else if (!this.showSelected && !this.showNotSelected) {
        args.columns = 'none';
      }
      const url = CSVService.validatedDownloadUrl(this.dataset.id, args);
      download(url, `${this.dataset.name}_Table`);
    },
    downloadMetabolites() {
      const metabolites = this.filteredColumnNames;

      downloadCSV(`Metabolites\n${metabolites.map(d => d.text).join('\n')}`, `${this.dataset.name}_Metabolites`);
    },
    downloadSamples() {
      const samples = this.filteredRowNames;

      downloadCSV(`Samples\n${samples.map(d => d.text).join('\n')}`, `${this.dataset.name}_Samples`);
    },
  },
};
</script>

<template lang="pug">
v-layout.download-component(row, fill-height)
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Metabolite Filter
      v-card.mx-3(flat)
        v-card-actions.vertical
          v-checkbox.my-0(v-model="showSelected",
              :label="`Selected (${countSelected})`", hide-details, color="#ffa500")
          v-checkbox.my-0(v-model="showNotSelected",
              :label="`Not Selected (${countNotSelected})`", hide-details, color="#4682b4")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Sample Filter
      v-card.mx-3(flat)
        v-card-actions.vertical
          v-checkbox.my-0(v-for="level in groupLevels", :key="level.name",
              :input-value="!hiddenGroups.includes(level.name)",
              @change="setLevelVisible(level, $event)",
              :label="`${level.name} (${level.count})`", hide-details, :color="level.color")

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Options
      v-card.mx-3(flat)
        v-card-actions.vertical
          v-checkbox.my-0(v-model="transpose", label="Transpose Table", hide-details)

      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Download
      v-card.mx-3(flat)
        v-card-actions.vertical
          v-btn.my-0.mx-0(text, flat, @click="downloadTable")
            v-icon {{$vuetify.icons.fileDownload}}
            | Table
          v-btn.my-0.mx-0(text, flat, @click="downloadMetabolites")
            v-icon {{$vuetify.icons.fileDownload}}
            | Metabolite List
          v-btn.my-0.mx-0(text, flat, @click="downloadSamples")
            v-icon {{$vuetify.icons.fileDownload}}
            | Sample List

  v-layout(v-if="!dataset || !ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Data Set

  data-table.download_table(v-else-if="ready", :row-headers="rowHeaders",
      :columns="columns", :cell-classes="cellClasses", :corner="corner")
</template>

<style scoped lang="scss">
.download-component {
  background: #eee;
}
.download_table {
  flex: 1 1 0;
}

.vertical {
  flex-direction: column;
  align-items: flex-start;
}

</style>
