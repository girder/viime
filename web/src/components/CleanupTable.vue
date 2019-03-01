<script>
import { mapState } from 'vuex';
import { SET_AXIS_LABEL } from '../store/mutations.type';

const menuOptions = [
  'data',
  'primary-key',
  'secondary-key',
  'disabled',
];

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      menuOptions,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.datasetId); },
  },
  methods: {
    selectOption(value, index, axis) {
      this.$store.commit(SET_AXIS_LABEL, {
        key: this.datasetId,
        axis,
        index,
        value,
        isPrimary: value === 'primary-key',
      });
    },
    getDisplayValue(axis, idx) {
      const val = this.dataset.axislabels[axis].labels[idx - 1];
      return val === 'data' ? `${idx}` : val;
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
        th.control(v-for="idx in dataset.width") 
          select.pa-1(
              :value="getDisplayValue('col', idx)",
              @input="selectOption($event.target.value, idx - 1, 'col')")
            option(style="display: none;") {{ idx }}
            option(
                v-for="option in menuOptions",
                :value="option",
                :key="`col${idx}${option}`") {{ option }} 

    tbody
      tr(v-for="(row, idx) in dataset.sourcerows",
          :key="`${idx}${row[0]}`",
          :class="dataset.axislabels.row.labels[idx]",)
        td.control
          select.pa-1(
              :value="getDisplayValue('row', idx + 1)",
              @input="selectOption($event.target.value, idx, 'row')")
            option(style="display: none;") {{ idx + 1 }}
            option(
                v-for="option in menuOptions",
                :value="option",
                :key="`row${idx}${option}`") {{ option }} 
        td.px-1.row(
            :class="dataset.axislabels.col.labels[idx2]"
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
  &.primary-key {
    background-color: #03b803;
  }
  &.secondary-key {
    background-color: lightgreen;
  }

  &.primary-key, &.secondary-key {
    td.primary-key, td.secondary-key {
      background-color: lightgray;
    }
  }
  td {
    &.primary-key {
      background-color: cyan;
    }
    &.secondary-key {
      background-color: lightblue;
    }
  }
  &.disabled td, td.disabled {
    background-color: lightgray !important;
  }
}


</style>
