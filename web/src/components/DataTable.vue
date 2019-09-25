<template lang="pug">
.data-table
  recycle-scroller.scroller(:items="columns", :item-size="80",
      key-field="index", direction="horizontal")
    template(#before)
      .column-header
        .column-header-cell
        .row-header-cell(v-for="(r,i) in rowHeaders", :key="i",
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
    rowHeaders() {
      return this.dataset.row.labels.map(
        (rowType, i) => this.createHeader(rowType, defaultRowOption, i + 1)
      );
    },
    selectedRanges() {
      return this.selected.ranges;
    },
    selectedType() {
      return this.selected.type;
    },
    columns() {
      const rows = this.dataset.sourcerows;
      return this.dataset.column.labels.map((colType, i) => {
        const column = {
          index: i,
          header: this.createHeader(colType, defaultColOption, base26Converter(i + 1)),
          clazz: [`type-${colType}`],
          values: rows.map(row => row[i]),
        };
        return column;
      });
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
    cellClasses(row, column, columnIndex, rowIndex) {
      const rowType = this.dataset.row.labels[rowIndex];
      return [`type-${rowType}`];
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
  background-color: $background;
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

.type-key {
  background-color: var(--v-primary-lighten3);
}

.type-metadata {
  background-color: var(--v-accent2-lighten3);
}

.type-group {
  background-color: var(--v-accent3-lighten3);
}

.type-header {
  background-color: var(--v-accent-lighten1);
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
