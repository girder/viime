<template lang="pug">
.data-table
  recycle-scroller.scroller(:items="columns", :item-size="80",
      key-field="index", direction="horizontal")
    template(#before)
      .column-header
        .column-header-cell
        .row-header-cell(v-for="(r,i) in rowHeaders", :key="i",
            :class="r.clazz", @click="onRowClick($event, i)")
          | {{r.text}}
    template(#default="{ item, index }")
      .column(:class="item.clazz")
        .column-header-cell(:class="item.header.clazz", @click="onColumnClick($event, index)")
          | {{item.header.text}}
        .cell(v-for="(r,i) in item.values", :key="i", :class="cellClasses(i)",
            :style="cellStyles(i, index, r)", @click="onCellClick($event, i, index)") {{r}}
</template>

<script>
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import { RecycleScroller } from 'vue-virtual-scroller';

import { base26Converter, textColor } from '../utils';
import { defaultRowOption, defaultColOption } from '../utils/constants';

export default {
  components: {
    RecycleScroller,
  },
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
    selected: {
      type: Object,
      required: true,
    },
  },
  computed: {
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
      const f = v => (typeof v === 'number' ? v.toFixed(3) : v);

      return this.dataset.column.labels.map((colType, i) => {
        const column = {
          index: i,
          header: this.createHeader(colType, defaultColOption, base26Converter(i + 1)),
          clazz: [`type-${colType}`],
          values: rows.map(row => f(row[i])),
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
      return group => lookup.get(group) || null;
    },
  },
  methods: {
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
    cellStyles(rowIndex, columnIndex, value) {
      const columnType = this.dataset.column.labels[columnIndex];
      const rowType = this.dataset.row.labels[rowIndex];
      if (columnType !== 'group' || rowType !== 'sample') {
        return null;
      }
      const color = this.groupToColor(value);
      const tColor = textColor(color);
      return {
        backgroundColor: color,
        color: tColor === 'black' ? null : tColor, // avoid setting default color
      };
    },
    setSelection(selection) {
      this.$emit('setselection', selection);
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
    onRowClick(event, rowIndex) {
      this.setSelection({
        key: this.id,
        event,
        axis: 'row',
        idx: rowIndex,
      });
    },
    onColumnClick(event, columnIndex) {
      this.setSelection({
        key: this.id,
        event,
        axis: 'column',
        idx: columnIndex,
      });
    },
    onCellClick(event, rowIndex, columnIndex) {
      const columnType = this.dataset.column.labels[columnIndex];
      const rowType = this.dataset.row.labels[rowIndex];
      if (rowType === 'header') {
        this.onColumnClick(event, columnIndex);
      } else if (columnType === 'key') {
        this.onRowClick(event, rowIndex);
      }
    },
  },
};
</script>

<style scoped lang="scss">
$background: #fafafa;
$selectionInner: rgba(161, 213, 255, 0.4);
$selectionBorder: rgb(23, 147, 248);
$selectionBorderWidth: 2px;
$selectionBorderWidth2: calc(100% - #{$selectionBorderWidth});

.data-table {
  position: relative;
  background-color: $background;
  user-select: none !important;
}

.scroller {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  right: 0;
}

.column {
  width: 80px;
}

.row-header-cell,
.column-header-cell,
.cell {
  height: 25px;
  padding: 2px 7px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}


.column-header-cell {
  text-align: center;
  background-color: $background;
  position: sticky;
  top: 0;
  z-index: 1;
  cursor: pointer;
}

.row-header-cell {
  background-color: $background;
  cursor: pointer;
}

// selection highlights
.active {
  background: linear-gradient(
    0deg,
    $selectionInner,
    $selectionInner
  );

  &.columnFirst {
    background: linear-gradient(
      90deg,
      $selectionBorder 0px,
      $selectionInner $selectionBorderWidth
    );
  }

  &.columnLast {
    background: linear-gradient(
      90deg,
      $selectionInner 0px,
      $selectionInner $selectionBorderWidth2,
      $selectionBorder 100%
    );
  }

  &.columnFirst.columnLast {
    background: linear-gradient(
      90deg,
      $selectionBorder 0px,
      $selectionInner $selectionBorderWidth,
      $selectionInner $selectionBorderWidth2,
      $selectionBorder 100%
    );
  }

  &.rowFirst {
    background: linear-gradient(
      180deg,
      $selectionBorder 0px,
      $selectionInner $selectionBorderWidth
    );
  }

  &.rowLast {
    background: linear-gradient(
      180deg,
      $selectionInner 0px,
      $selectionInner $selectionBorderWidth2,
      $selectionBorder 100%
    );
  }

  &.rowFirst.rowLast {
    background: linear-gradient(
      180deg,
      $selectionBorder 0px,
      $selectionInner $selectionBorderWidth,
      $selectionInner $selectionBorderWidth2,
      $selectionBorder 100%
    );
  }
}

@mixin selectionAware($color) {
  background-color: $color;

  &.active,
  &.active.columnFirst,
  &.active.columnLast,
  &.active.columnFirst.columnLast,
  &.active.rowFirst,
  &.active.rowLast,
  &.active.rowFirst.rowLast {
    background-color: $color;
  }
}

// column
.type-key {
  @include selectionAware(var(--v-primary-lighten3));
  cursor: pointer;
}
// column, row
.type-metadata {
  @include selectionAware(var(--v-accent2-lighten3));
}
// column
.type-group {
  @include selectionAware(var(--v-accent3-lighten3));
}
// row
.type-header {
  @include selectionAware(var(--v-accent-lighten1));
  color: white;
  font-weight: 700;
  position: sticky;
  top: 25px;
  cursor: pointer;
}
// column, row
.type-masked {
  @include selectionAware(var(--v-secondary-lighten2));
  font-weight: 300;
  color: var(--v-secondary-base);
}
// column, row
.type-sample {
  text-align: right;
}

</style>
<style scoped>
.scroller >>> .vue-recycle-scroller__slot {
  position: sticky;
  left: 0;
  z-index: 1;
}
.scroller >>> .vue-recycle-scroller__item-wrapper {
  overflow: unset;
}
.scroller >>> .vue-recycle-scroller__item-view {
  overflow: unset;
}
</style>
