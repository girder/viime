<script>
const menuOptions = [
  'primary-key',
  'secondary-key',
  'disable',
  'enable',
];

export default {
  props: {
    rows: {
      type: Array,
      required: true,
    },
    metadata: {
      /**
       * width,
       * height,
       * rows, // samples
       * colmeta, // measurements
       */
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      menuOptions,
    };
  },
  methods: {
    selectOption(value, idx, axis) {
      const newaxis = [...this.metadata[axis]];
      newaxis[idx] = [ value ];
      this.$emit('update:metadata', {
        ...this.metadata,
        [axis]: newaxis,
      });
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
        th.control(v-for="idx in metadata.width") 
          select.pa-1(@input="selectOption($event.target.value, idx - 1, 'cols')")
            option {{ idx }}
            option(
                v-for="option in menuOptions",
                :value="option",
                :key="`col${idx}${option}`") {{ option }} 

    tbody
      tr(v-for="(row, idx) in rows",
          :key="`${idx}${row[0]}`",
          :class="metadata.rows[idx]",)
        td.control
          select.pa-1(@input="selectOption($event.target.value, idx, 'rows')")
            option {{ idx + 1 }}
            option(
                v-for="option in menuOptions",
                :value="option",
                :key="`row${idx}${option}`") {{ option }} 
        td.px-1.row(
            :class="metadata.cols[idx2]"
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
  &.disable td {
    background-color: lightgray !important;
  }
}


</style>
