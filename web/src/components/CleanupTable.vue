<script>
const menuOptions = [
  'Primary',
  'Secondary',
  'Disable',
  'Enable',
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
       * rowmeta, // samples
       * colmeta, // measurements
       */
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      popover: false,
      popover_x: 0,
      popover_y: 0,
      menuOptions,
    };
  },
  methods: {
    showPopover(event, rowcol, idx) {
      console.log(event);
      setTimeout(() => {
        this.popover_x = event.pageX + 10;
        this.popover_y = event.pageY + 10;
        this.popover = true;
      }, this.popover ? 50 : 0);
      if (this.popover) this.popover = false;
    },
    selectOption(event, option) {
      this.popover = false;
    }
  },
};
</script>

<template lang="pug">
.cleanup-wrapper
  table.cleanup-table
    thead
      tr
        th <!--empty-->
        th.control(v-for="idx in metadata.width") 
          select
            option {{ idx }}
            option(v-for="option in menuOptions" :value="option") {{ option }} 
          //- span {{ idx }}
          //- v-icon(@click="showPopover($event, 'col', idx)") {{ $vuetify.icons.menuDown }}
    tbody
      tr(v-for="(row, idx) in rows")
        td.control
          select
            option {{ idx }}
            option(v-for="option in menuOptions" :value="option") {{ option }} 
          //- span.px-2 {{ idx + 1 }}
          //- v-icon(@click="showPopover($event, 'row', idx)") {{ $vuetify.icons.menuDown }}
        td.px-1(v-for="col in row") {{ col }}
  v-menu(:value="popover", :position-x="popover_x", :position-y="popover_y")
    v-list
      v-list-tile(v-for="option in menuOptions" @click="selectOption($event, option)")
        v-list-tile-title {{ option }}
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
      // border-radius: 5px;
      min-width: 100px;
      font-weight: 700;
      cursor: pointer;
      span {
        vertical-align: sub;
        vertical-align: -webkit-baseline-middle;
      }
      i {
        float: right;
        border-left: 2px solid gray;
        border-radius: 5px;
      }
      select {
        // border: 0;
        width: 100%;
        appearance: menulist !important;
      }
    }
  }
}

</style>
