<script>
import { mapMutations } from 'vuex';
import { SET_SELECTION } from '@/store/mutations.type';
import {
  defaultRowOption,
  defaultColOption,
} from '@/utils/constants';
import { base26Converter, textColor, formatter } from '../utils';
import DataTable from './DataTable.vue';

export default {
  components: {
    DataTable,
  },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    selected() { return this.dataset.selected; },
    rowHeaders() {
      return this.dataset.row.labels.map(
        (rowType, i) => {
          const header = this.createHeader(rowType, defaultRowOption, i + 1);
          header.clazz.push(...this.getSelectionClasses('row', i));
          return header;
        },
      );
    },
    columns() {
      const rows = this.dataset.sourcerows;

      const rowTypes = this.dataset.row.labels;

      const f = (v, colType, rowType) => {
        if (colType !== 'measurement' || rowType !== 'sample') {
          return v;
        }
        return formatter(v);
      };

      return this.dataset.column.labels.map((colType, i) => {
        const column = {
          index: i,
          header: this.createHeader(colType, defaultColOption, base26Converter(i + 1)),
          clazz: [`type-${colType}`],
          values: rows.map((row, r) => f(row[i], colType, rowTypes[r])),
        };
        const selected = this.getSelectionClasses('column', i);
        column.clazz.push(...selected);
        column.header.clazz.push(...selected);
        return column;
      });
    },
    groupToColor() {
      const levels = this.dataset.groupLevels;
      const lookup = new Map(levels.map(({ name, color }) => [name, color]));
      return (group) => lookup.get(group) || null;
    },
  },
  methods: {
    ...mapMutations({ setSelection: SET_SELECTION }),

    createHeader(type, defaultType, text) {
      const header = {
        text,
        clazz: [`type-${type}`],
      };
      if (type !== defaultType) {
        // icon
        header.text = '';
        header.clazz.push('mdi', this.$vuetify.icons[type]);
      }
      return header;
    },
    cellClasses(rowIndex) {
      const rowType = this.dataset.row.labels[rowIndex];
      return [`type-${rowType}`, ...this.getSelectionClasses('row', rowIndex)];
    },
    getSelectionClasses(axis, index) {
      if (this.selected.type !== axis) {
        return [];
      }
      const includes = this.selected.ranges.includes(index);
      const classList = [];
      if (includes.member) {
        classList.push('active');
      }
      if (includes.first) {
        classList.push(`${axis}First`);
      }
      if (includes.last) {
        classList.push(`${axis}Last`);
      }
      return classList;
    },
    onRowClick({ event, rowIndex }) {
      this.setSelection({
        key: this.dataset.id,
        event,
        axis: 'row',
        idx: rowIndex,
      });
    },
    onColumnClick({ event, columnIndex }) {
      this.setSelection({
        key: this.dataset.id,
        event,
        axis: 'column',
        idx: columnIndex,
      });
    },
    onCellClick({ event, rowIndex, columnIndex }) {
      const columnType = this.dataset.column.labels[columnIndex];
      const rowType = this.dataset.row.labels[rowIndex];
      if (rowType === 'header') {
        this.onColumnClick({ event, columnIndex });
      } else if (columnType === 'key') {
        this.onRowClick({ event, rowIndex });
      }
    },
    cellStyles(rowIndex, columnIndex, value) {
      const columnType = this.dataset.column.labels[columnIndex];
      const rowType = this.dataset.row.labels[rowIndex];
      if (columnType !== 'group' || rowType !== 'sample') {
        return null;
      }
      const color = this.groupToColor(String(value));
      const tColor = textColor(color);
      return {
        backgroundColor: color,
        color: tColor === 'black' ? null : tColor, // avoid setting default color
      };
    },
    showTooltip(rowIndex, columnIndex) {
      const columnType = this.dataset.column.labels[columnIndex];
      const rowType = this.dataset.row.labels[rowIndex];
      return columnType !== 'measurement' || rowType !== 'sample';
    },
  },
};
</script>

<template lang="pug">
data-table(:row-headers="rowHeaders", :columns="columns",
    :cell-classes="cellClasses", :cell-styles="cellStyles",
    @row-click="onRowClick($event)", :show-tooltip="showTooltip",
    :header-tooltips="false",
    @column-click="onColumnClick($event)", @cell-click="onCellClick($event)")
</template>
