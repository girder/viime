<script>
import { CHANGE_AXIS_LABEL } from '@/store/actions.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
} from '@/utils/constants';
import { base26Converter } from '@/utils';

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      tagOptions: {
        row: rowMenuOptions,
        column: colMenuOptions,
      },
      selected: { type: 'column', index: 1 },
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.datasetId); },
  },
  methods: {
    base26Converter,
    async selectOption(label, index, axis_name) {
      await this.$store.dispatch(CHANGE_AXIS_LABEL, {
        dataset_id: this.datasetId,
        axis_name,
        label,
        index,
      });
      this.selected = { type: this.selected.type, index: this.selected.index + 1 };
    },
    getDisplayValue(axis, idx) {
      const val = this.dataset[axis].labels[idx];
      if (axis === 'row') return val === defaultRowOption ? `${idx + 1}` : val;
      if (axis === 'column') return val === defaultColOption ? `${idx + 1}` : val;
      throw new Error(`${axis} is not a valid axis name`);
    },
    isActive(index, axisName) {
      return this.selected.index === index
          && this.selected.type === axisName;
    },
  },
};
</script>

<template lang="pug">
.cleanup-wrapper

  v-layout(v-if="!dataset", fill-height, justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Table

  v-layout(v-else, fill-height, column)
    v-toolbar.primary(dense)
      v-btn-toggle(dark, mandatory,
          :active-class="'aktive'",
          :value="dataset[selected.type].labels[selected.index]",
          @change="selectOption($event, selected.index, selected.type)")
        v-btn(v-for="option in tagOptions[selected.type]",
            flat, :key="option.value", :value="option.value")
          v-icon.pr-1 {{ $vuetify.icons[option.icon] }}
          | {{ option.title }}

    .overflow-auto
      table.cleanup-table

        thead
          tr
            th
            th.control.px-2(
                v-for="(col, index) in dataset.column.labels",
                :class="{ 'active': isActive(index, 'column') }",
                @click="selected = { type: 'column', index }")
              | {{ base26Converter(index + 1) }}

        tbody
          tr.datarow(v-for="(row, index) in dataset.sourcerows",
              :key="`${index}${row[0]}`",
              :class="{[dataset.row.labels[index]]: true, 'active': isActive(index, 'row')}")
            td.control.px-2(@click="selected = { type: 'row', index }") {{ index + 1 }}
            td.px-2.row(
                v-for="(col, idx2) in row",
                :class="{[dataset.column.labels[idx2]]: true, 'active': isActive(idx2, 'column')}",
                :key="`${index}.${idx2}`") {{ col }}
</template>

<style lang="scss" scoped>
.cleanup-wrapper {
  width: 100%;

  .v-btn--active {
    background-color: #607d8b;
  }

  .cleanup-table {
    border-spacing: 0px;

    .key, .metadata, .header, .group {
      font-weight: 700;
      color: white;
      text-align: left;
    }

    tr.active td, td.active {
      background-color:  #81D4FA !important;
    }

    th, td {
      white-space: nowrap;
      padding: 2px;
      text-align: center;

      &.control {
        cursor: pointer;
        font-weight: 300;
      }
    }

    th:nth-child(odd):not(.masked) {
      background-color: #dae1e4;
    }

    tr:nth-child(odd):not(.masked) {
      background-color: #ECEFF1;

      &.datarow td:nth-child(odd) {
        background-color: rgb(218, 225, 228);
      }
    }

    tr.datarow:not(.masked) {
      &.header {
        td:nth-child(odd):not(.masked) {
          background-color: #8BC34A;
        }

        td:nth-child(even):not(.masked) {
          background-color: #9CCC65;
        }
      }

      &.metadata {
        td:nth-child(odd) {
          background-color: #9E9E9E;
        }

        td {
          background-color: #BDBDBD;
        }
      }

      &.header, &.metadata {
        .key, .metadata, .group {
          background-color: lightgray;
          font-weight: 300;
          color: black;
        }
      }

      &:nth-child(odd) {
        td.key {
          background-color: #546E7A;
        }

        td.metadata, td.group {
          background-color: #9E9E9E;
        }
      }

      td {
        &:nth-child(odd) {
          background-color: rgba(236, 239, 241, 0.4);

          &.masked {
            background-color: lightgray ;
          }
        }

        &.key {
          background-color: #78909C;
        }

        &.metadata,&.group {
          background-color: #BDBDBD;
        }
      }
    }

    tr {
      &.masked td, td.masked, th.masked {
        background-color: lightgray ;
      }
    }
  }
}

</style>
