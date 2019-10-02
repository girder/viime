<script>
import { mapMutations } from 'vuex';
import { CHANGE_AXIS_LABEL } from '@/store/actions.type';
import { SET_SELECTION } from '@/store/mutations.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
} from '@/utils/constants';
import { base26Converter } from '@/utils';
import SaveStatus from '@/components/SaveStatus.vue';
import DataTable from '@/components/DataTable.vue';


export default {
  components: {
    DataTable,
    SaveStatus,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      privateTagOptions: {
        row: rowMenuOptions,
        column: colMenuOptions,
      },
      defaultColOption,
      defaultRowOption,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    selected() { return this.dataset.selected; },
    radioValue() {
      const { type, ranges } = this.selected;
      const { members } = ranges;
      const types = members.map(m => this.dataset[type].labels[m]);
      const unique = [...new Set(types)];
      return unique.length === 1 ? unique[0] : null;
    },
    tagOptions() {
      return this.privateTagOptions[this.selected.type]
        .filter(option => (this.selected.ranges.members.length > 1 ? !option.mutex : true));
    },
    selectedString() {
      const { members } = this.selected.ranges;
      const multi = members.length > 1;
      if (multi) {
        return `${members.length} ${this.selected.type}s selected`;
      }
      if (this.selected.type === 'row') {
        return `Row ${members[0] + 1}`;
      }
      return `Column ${base26Converter(members[0] + 1)}`;
    },
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
  },
  methods: {
    ...mapMutations({ setSelection: SET_SELECTION }),
    base26Converter,
    async selectOption(label) {
      const { ranges, type: context } = this.selected;
      const changes = ranges.members.map(index => ({ context, index, label }));
      await this.$store.dispatch(CHANGE_AXIS_LABEL, { dataset_id: this.id, changes });
    },

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
        key: this.id,
        event,
        axis: 'row',
        idx: rowIndex,
      });
    },
    onColumnClick({ event, columnIndex }) {
      this.setSelection({
        key: this.id,
        event,
        axis: 'column',
        idx: columnIndex,
      });
    },
    onCellClick({ event, rowIndex, columnIndex }) {
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

<template lang="pug">
v-layout.cleanup-wrapper(row)

  router-view

  v-layout(v-if="!dataset || !dataset.ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Table

  v-layout(v-else, column)
    v-toolbar.radio-toolbar(dense)

      v-toolbar-title.ml-3.radio-title
        .subheading.font-weight-bold.primary--text.text--lighten-1  SELECT DATA TYPE
        .primary--text.text--darken-3.body-2(style="margin-top: -8px;") {{ selectedString }}
      v-divider.mx-2(vertical, inset)
      v-radio-group.mx-2.radio-group(mandatory, row, hide-details,
          :value="radioValue",
          @change="selectOption")
        v-radio.my-1(v-for="option in tagOptions",
            color="primary darken-3",
            :value="option.value",
            :label="option.title",
            :key="option.value")
          template(#label)
            span {{ option.title }}
            v-icon.radio-icon.mdi-light(small, :class="option.color")
              | {{ $vuetify.icons[option.icon] }}

      v-spacer

      save-status

    data-table.cleanup-table(:row-headers="rowHeaders", :columns="columns",
        :cell-classes="cellClasses", @row-click="onRowClick($event)",
        @column-click="onColumnClick($event)", @cell-click="onCellClick($event)")
</template>

<style lang="scss">
.cleanup-wrapper {
  width: 100%;

  .radio-toolbar {
    z-index: 2;

    .v-toolbar__content {
      height: inherit !important;
      padding: 0px;
    }

    .v-input--selection-controls__input {
      margin-right: 2px;
    }

    .radio-group {
      padding-top: 0px;
    }

    .v-radio {
      border-radius: 3px;
      padding: 2px;
      background-color: #dde0e1; // TODO: find a better way to get this color.

      .v-label {
        color: var(--v-primary-darken3);
      }
    }

    .radio-title {
      min-width: 110px;
    }

    .v-divider {
      height: 32px;
    }

    .radio-icon {
      padding: 2px;
      border-radius: 3px;
      margin: 4px;
    }
  }

  .cleanup-table {
    flex: 1 1 0;
  }
}
</style>
