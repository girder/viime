<template lang="pug">
.data-table
  recycle-scroller.scroller(:items="columns", :item-size="80",
      key-field="index", direction="horizontal")
    template(#before)
      .column-header
        .column-header-cell
        .row-header-cell(v-for="(r,i) in rows", :key="i",
            :class="r.clazz") {{r.text}}
    template(#default="{ item, index }")
      .column(:class="item.clazz")
        .column-header-cell(:class="item.header.clazz") {{item.header.text}}
        .cell(v-for="(r,i) in item.values", :key="i", :class="cellClasses(r, item, index, i)") {{r}}
</template>

<script>
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import { RecycleScroller } from 'vue-virtual-scroller';

import { base26Converter } from '../utils';
import {
  defaultRowOption,
  defaultColOption,
} from '../utils/constants';

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
    rows() {
      return this.dataset.row.labels.map((rowType, i) => {
        if (rowType === defaultRowOption) {
          return { text: i + 1, clazz: [] };
        }
        // icon
        return {
          text: '',
          clazz: ['mdi', this.$vuetify.icons[rowType]],
        };
      });
    },
    selectedRanges() {
      return this.selected.ranges;
    },
    selectedType() {
      return this.selected.type;
    },
    columns() {
      return this.dataset.column.labels.map((colType, i) => {
        const column = {
          index: i,
          header: {
            text: base26Converter(i + 1),
            clazz: [],
          },
          values: [],
        };
        if (colType !== defaultColOption) {
          column.header.text = '';
          column.header.clazz.push('mdi', this.$vuetify.icons[colType]);
        }
        return column;
      });
    },
  },
  methods: {
    activeClasses(index, axisName) {
      if (axisName === this.selected.type) {
        const ranges = this.selectedRanges;
        const includes = ranges.includes(index);
        const classList = [];
        if (includes.member) {
          classList.push('active');
        }
        if (includes.first) {
          classList.push('first');
        }
        if (includes.last) {
          classList.push('last');
        }
        return classList;
      }
      return [];
    },
    columnClasses(column, index) {
      return [];
    },
    columnHeaderClasses(column, index) {
      return [];
    },
    cellClasses(row, column, columnIndex, rowIndex) {
      return [];
    },
    setSelection(selection) {
      this.$emit('setselection', selection);
    },
  },
};
</script>

<style scoped lang="scss">
$background: #fafafa;

.data-table {
  position: relative;
  background: $background;
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

.column-header {

}

.column-header-cell {
  text-align: center;
  background: $background;
  position: sticky;
  top: 0;
  z-index: 1;
  cursor: pointer;
}

.row-header-cell {
  background: $background;
  cursor: pointer;
}

.cell {

}

.row-header-cell,
.column-header-cell,
.cell {
  height: 25px;
  padding: 2px 7px;
  white-space: nowrap;
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
