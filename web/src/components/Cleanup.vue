<script>
import { CHANGE_AXIS_LABEL } from '@/store/actions.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
} from '@/utils/constants';
import { base26Converter, RangeList } from '@/utils';
import SaveStatus from '@/components/SaveStatus.vue';

export default {
  components: {
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
      selected: {
        type: 'column',
        last: 1,
        ranges: new RangeList([1]),
      },
      settingsDialog: false,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    radioValue() {
      const { type, last, ranges } = this.selected;
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
      } else {
        if (this.selected.type === 'row') {
          return `Row ${members[0] + 1}`;
        } else {
          return `Column ${base26Converter(members[0] + 1)}`;
        }
      }
    }
  },
  methods: {
    base26Converter,
    async selectOption(label) {
      const promises = [];
      const { ranges, type: axis_name } = this.selected;
      // TODO: Support batched operations
      ranges.members.forEach(index => {
        promises.push(this.$store.dispatch(CHANGE_AXIS_LABEL, {
          dataset_id: this.id,
          axis_name,
          label,
          index,
        }));
      });
      await Promise.all(promises);
    },
    activeClasses(index, axisName) {
      if (axisName === this.selected.type) {
        const includes = this.selected.ranges.includes(index);
        return {
          active: includes.member,
          first: includes.first,
          last: includes.last,
        };
      } else {
        return {};
      }
    },
    setSelection(event, axis, idx) {
      const { last, ranges, type } = this.selected;
      this.selected.last = idx;
      if (event.shiftKey && axis === type ) {
        ranges.add(last, idx);
      } else if (event.ctrlKey && axis === type) {
        ranges.add(idx);
      } else if (!event.ctrlKey && !event.shiftKey) {
        this.selected.ranges = new RangeList([idx]);
        this.selected.type = axis;
      }
    },
  },
};
</script>

<template lang="pug">
v-layout.cleanup-wrapper(row)

  router-view

  v-layout(v-if="!dataset", justify-center, align-center)
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
            span {{ option.value }}
            v-icon.radio-icon.mdi-light(small, :class="option.color")
              | {{ $vuetify.icons[option.icon] }}

      v-spacer

      save-status
      v-dialog(v-model="settingsDialog", max-width="500")
        template(v-slot:activator="{ on }")
          v-btn(icon, v-on="on")
            v-icon {{ $vuetify.icons.settings }}
        v-card
          v-card-title.headline Imputation Settings
          v-card-actions
            v-spacer
            v-btn(flat, @click="settingsDialog = false") Close
            v-btn(depressed) Save
      v-icon {{ $vuetify.icons.download }}

    .overflow-auto
      table.cleanup-table

        thead
          tr
            th
            th.control.px-2(
                v-for="(col, index) in dataset.column.labels",
                :class="activeClasses(index, 'column')",
                @click="setSelection($event, 'column', index)")
              span(v-if="col === defaultColOption") {{ base26Converter(index + 1) }}
              v-icon(v-else, small) {{ $vuetify.icons[col] }}

        tbody
          tr.datarow(v-for="(row, index) in dataset.sourcerows",
              :key="`${index}${row[0]}`",
              :class="{[dataset.row.labels[index]]: true, ...activeClasses(index, 'row')}")
            td.control.px-2(@click="setSelection($event, 'row', index)")
              span(v-if="dataset.row.labels[index] === defaultRowOption") {{ index + 1 }}
              v-icon(v-else, small) {{ $vuetify.icons[dataset.row.labels[index]] }}
            td.px-2.row(
                v-for="(col, idx2) in row",
                :class="{[dataset.column.labels[idx2]]: true, ...activeClasses(idx2, 'column')}",
                :key="`${index}.${idx2}`") {{ col }}
</template>

<style lang="scss">
@mixin masked() {
  background-color: var(--v-secondary-lighten1);
  font-weight: 300;
  color: var(--v-secondary-darken1);
}

.cleanup-wrapper {
  width: 100%;

  .radio-toolbar {
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
    border-spacing: 0px;
    user-select: none;

    .key, .metadata, .header, .group {
      font-weight: 700;
      color: white;
      text-align: left;
    }

    tr {
      th, td {
        white-space: nowrap;
        padding: 2px;
        text-align: center;

        &.control {
          cursor: pointer;
          font-weight: 300;
        }
      }

      background-color: #fdfdfd;

      &:nth-child(odd) {
        background-color: var(--v-primary-lighten5);

        td:nth-child(odd), th:nth-child(odd) {
          background-color: #CFD8DC;
        }
      }
      
      td:nth-child(odd) {
        background-color: var(--v-primary-lighten5);
      }

      td.active, th.active {
        &.first {
          border-left: 2px solid var(--v-secondary-darken3);
        }

        &.last {
          border-right: 2px solid var(--v-secondary-darken3);
        }
      }

      &.active.first td {
        border-top: 2px solid var(--v-secondary-darken3);
      }

      &.active.last td{
        border-bottom: 2px solid var(--v-secondary-darken3);
      }

      &.active td,
      td.active {
        background: linear-gradient(0deg,rgba(161, 213, 255, 0.2),rgba(161, 213, 255, 0.2));
      }
    }

    tr.datarow {
      &.header {
        td:nth-child(odd) {
          background-color: var(--v-accent-base);
        }

        td {
          background-color:var(--v-accent-lighten1);
        }
      }

      &.metadata {
        td:nth-child(odd) {
          background-color: var(--v-accent2-lighten2);
        }

        td {
          background-color: var(--v-accent2-lighten3);
        }
      }

      &.header,
      &.header:nth-child(odd),
      &.metadata,
      &.metadata:nth-child(odd) {
        td.key, td.metadata, td.group {
          @include masked();
        }
      }

      &:nth-child(odd) {
        td.key {
          background-color: var(--v-primary-lighten1);
        }

        td.metadata {
          background-color: var(--v-accent2-lighten3);
        }
        
        td.group {
          background-color: var(--v-accent3-lighten2);
        }
      }

      td {
        &.key {
          background-color: var(--v-primary-base);
        }

        &.metadata, {
          background-color: var(--v-accent2-lighten2);
        }

        &.group {
          background-color: var(--v-accent3-lighten1);
        }
      }
    }

    tr.datarow,
    tr.datarow:nth-child(odd) {
      &.masked td,
      td.masked:nth-child(odd),
      td.masked,
      th.masked {
        @include masked();
      }
    }
  }
}

</style>
