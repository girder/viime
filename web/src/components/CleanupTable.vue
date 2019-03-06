<script>
import { mapState } from 'vuex';
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
    selectOption(label, index, axis) {
      this.$store.dispatch(CHANGE_AXIS_LABEL, {
        dataset_id: this.datasetId,
        axis, label, index });
    },
    getDisplayValue(axis, idx) {
      const val = this.dataset[axis].labels[idx];
      if (axis === 'row')
        return val === defaultRowOption ? `${idx + 1}` : val;
      else if (axis === 'column')
        return val === defaultColOption ? `${idx + 1}` : val;
    }
  },
};
</script>

<template lang="pug">
.cleanup-wrapper
  table.cleanup-table
    
    thead
      tr
        th <!-- empty -->
        th.control(v-for="(col, idx) in dataset.column.labels") 
          select.pa-1(
              :value="getDisplayValue('column', idx)",
              @input="selectOption($event.target.value, idx, 'column')")
            option(style="display: none;") {{ idx + 1 }}
            option(
                v-for="option in colMenuOptions",
                :value="option",
                :key="`column${idx}${option}`") {{ option }}
            option(v-show="dataset['column'].labels[idx] !== colPrimaryKey") masked

    tbody
      tr(v-for="(row, idx) in dataset.sourcerows",
          :key="`${idx}${row[0]}`",
          :class="dataset.row.labels[idx]",)
        td.control
          select.pa-1(
              :value="getDisplayValue('row', idx)",
              @input="selectOption($event.target.value, idx, 'row')")
            option(style="display: none;") {{ idx + 1 }}
            option(
                v-for="option in rowMenuOptions",
                :value="option",
                :key="`row${idx}${option}`") {{ option }}
            option(v-show="dataset['row'].labels[idx] !== rowPrimaryKey") masked
        td.px-1.row(
            :class="dataset.column.labels[idx2]"
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

  th, td {
    white-space: nowrap;
    border: 2px solid gray;
    
    &.control {
      background-color: lightgray;
      // border-radius: 5px;
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

tr {
  &.header {
    background-color: #03b803;
  }
  &.metadata {
    background-color: lightgreen;
  }

  &.header, &.metadata {
    td.header, td.metadata {
      background-color: lightgray;
    }
  }
  td {
    &.key {
      background-color: cyan;
    }
    &.metadata {
      background-color: lightblue;
    }
  }
  &.masked td, td.masked {
    background-color: lightgray !important;
  }
}


</style>
