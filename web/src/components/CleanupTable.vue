<script>
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
       * rowmeta, // samples
       * colmeta, // measurements
       */
      type: Object,
      required: true,
    },
  },
  computed: {

  },
};
</script>

<template lang="pug">
.cleanup-wrapper
  table.cleanup-table
    thead
      tr
        th <!--empty-->
        th.control(v-for="i in metadata.width") 
          span {{ i }}
          v-icon {{ $vuetify.icons.menuDown }}
    tbody
      tr(v-for="(row, idx) in rows")
        td.control
          span.px-2 {{ idx + 1 }}
          v-icon {{ $vuetify.icons.menuDown }}
        td.pa-1(v-for="col in row") {{ col }}
</template>

<style lang="scss" scoped>
.cleanup-wrapper {
  width: 100%;
}
.cleanup-table {
  overflow: auto;
  display: block;
  height: 100%;
  border-spacing: 4px;
  th, td {
    white-space: nowrap;
    
    &.control {
      background-color: lightgray;
      border-radius: 5px;
      min-width: 80px;
      font-weight: 700;
      cursor: pointer;
      span {
        vertical-align: sub;
        vertical-align: -webkit-baseline-middle;
      }
      i {
        float: right;
        border-left: 2px solid gray;
        border-radius: 10px;
      }
    }
  }
}

</style>
