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
        .cell(v-for="(r,i) in item.values", :key="i", :class="cellClasses(i, index)",
            @click="onCellClick($event, i, index)") {{r}}
</template>

<script>
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import { RecycleScroller } from 'vue-virtual-scroller';

export default {
  components: {
    RecycleScroller,
  },
  props: {
    rowHeaders: { // {text: string, clazz?: string[]}[]
      type: Array,
      required: true,
    },
    columns: { // {index: number, header: ..., clazz?: string[], values: string[]}[]
      type: Array,
      required: true,
    },
    cellClasses: { // (rowIndex: number, columnIndex: number) => string[]
      type: Function,
      required: true,
    },
  },
  methods: {
    setSelection(selection) {
      this.$emit('setselection', selection);
    },
    onRowClick(event, rowIndex) {
      this.$emit('row-click', { event, rowIndex });
    },
    onColumnClick(event, columnIndex) {
      this.$emit('column-click', { event, columnIndex });
    },
    onCellClick(event, rowIndex, columnIndex) {
      this.$emit('cell-click', { event, rowIndex, columnIndex });
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

  &.column-header-cell {
    top: 0;
  }
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
