<script>
import { CHANGE_AXIS_LABEL } from '../store/actions.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
  rowPrimaryKey,
  colPrimaryKey,
} from '../utils/constants';

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      rowMenuOptions,
      colMenuOptions,
      rowPrimaryKey,
      colPrimaryKey,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.datasetId); },
  },
  methods: {
    selectOption(label, index, axis_name) {
      this.$store.dispatch(CHANGE_AXIS_LABEL, {
        dataset_id: this.datasetId,
        axis_name,
        label,
        index,
      });
    },
    getDisplayValue(axis, idx) {
      const val = this.dataset[axis].labels[idx];
      if (axis === 'row') return val === defaultRowOption ? `${idx + 1}` : val;
      if (axis === 'column') return val === defaultColOption ? `${idx + 1}` : val;
      throw new Error(`${axis} is not a valid axis name`);
    },
  },
};
</script>

<template lang="pug">
.cleanup-wrapper
  v-layout(v-if="!dataset", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")

  table.cleanup-table(v-else)
    thead
      tr.controlrow
        th
        th.control(v-for="(col, idx) in dataset.column.labels")
          select.pa-1(
              :value="getDisplayValue('column', idx)",
              @input="selectOption($event.target.value, idx, 'column')")
            option(style="display: none;") {{ idx + 1 }}
            option(
                v-for="option in colMenuOptions",
                :value="option",
                :key="`column${idx}${option}`") {{ option }}
    tbody
      tr.datarow(v-for="(row, idx) in dataset.sourcerows",
          :key="`${idx}${row[0]}`",
          :class="dataset.row.labels[idx]")
        td.control
          select.pa-1(
              :value="getDisplayValue('row', idx)",
              @input="selectOption($event.target.value, idx, 'row')")
            option(style="display: none;") {{ idx + 1 }}
            option(
                v-for="option in rowMenuOptions",
                :value="option",
                :key="`row${idx}${option}`") {{ option }}
        td.px-1.row(
            :class="dataset.column.labels[idx2]",
            v-for="(col, idx2) in row",
            :key="`${idx}.${idx2}`") {{ col }}
</template>

<style lang="scss" scoped>
.cleanup-wrapper {
  width: 100%;
}
.cleanup-table {
  overflow: auto;
  display: block;
  margin: auto;
  height: 100%;
  border-collapse: collapse;

  .key, .metadata, .header, .group {
    font-weight: 700;
    color: white;
    text-align: left;
  }

  th, td {
    white-space: nowrap;
    padding: 2px;
    text-align: center;

    &.control {
      background-color: lightgray !important;
      color: black;
      min-width: 100px;
      font-weight: 700;
      cursor: pointer;

      select {
        width: 100%;
        appearance: menulist !important;
      }
    }
  }
}

tr:nth-child(odd) {
  background-color: #ECEFF1;

  &.datarow td:nth-child(odd) {
    background-color: rgb(218, 225, 228);
  }
}

tr.datarow {
  &.header {
    td:nth-child(odd) {
      background-color: #8BC34A;
    }
    td:nth-child(even) {
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
      background-color: lightgray !important;
      font-weight: 300;
      color: black;
    }
  }

  &:nth-child(odd) {
    td.key {
      background-color: #546E7A;
    }

    td.metadata,td.group {
      background-color: #9E9E9E;
    }
  }

  td {
    &:nth-child(odd) {
      background-color: rgba(236, 239, 241, 0.4);
    }

    &.key {
      background-color: #78909C;
    }
    &.metadata,&.group {
      background-color: #BDBDBD;
    }
  }

  &.masked td, td.masked {
    background-color: lightgray !important;
  }
}


</style>
