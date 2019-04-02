<script>
import { CHANGE_AXIS_LABEL } from '@/store/actions.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
} from '@/utils/constants';
import { base26Converter } from '@/utils';
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
      tagOptions: {
        row: rowMenuOptions,
        column: colMenuOptions,
      },
      defaultColOption,
      defaultRowOption,
      selected: { type: 'column', index: 1 },
      settingsDialog: false,
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
  },
  methods: {
    base26Converter,
    async selectOption(label, index, axis_name) {
      await this.$store.dispatch(CHANGE_AXIS_LABEL, {
        dataset_id: this.id,
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
    isActive(index, axisName) {
      return this.selected.index === index
          && this.selected.type === axisName;
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
        .subheading.font-weight-bold.secondary--text.text--lighten-1  SELECT DATA TYPE
        .body-2(style="margin-top: -8px;")
          | {{ selected.type }}
          | {{ selected.type === 'row' ? selected.index+1 : base26Converter(selected.index+1) }}
      v-divider.mx-2(vertical, inset)
      v-radio-group.mx-2.radio-group(mandatory, row, hide-details,
          :value="dataset[selected.type].labels[selected.index]",
          @change="selectOption($event, selected.index, selected.type)")
        v-radio.grey.lighten-2.my-1(v-for="option in tagOptions[selected.type]",
            color="black",
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

    .overflow-auto
      table.cleanup-table

        thead
          tr
            th
            th.control.px-2(
                v-for="(col, index) in dataset.column.labels",
                :class="{ 'active': isActive(index, 'column') }",
                @click="selected = { type: 'column', index }")
              span(v-if="col === defaultColOption") {{ base26Converter(index + 1) }}
              v-icon(v-else, small) {{ $vuetify.icons[col] }}

        tbody
          tr.datarow(v-for="(row, index) in dataset.sourcerows",
              :key="`${index}${row[0]}`",
              :class="{[dataset.row.labels[index]]: true, 'active': isActive(index, 'row')}")
            td.control.px-2(@click="selected = { type: 'row', index }")
              span(v-if="dataset.row.labels[index] === defaultRowOption") {{ index + 1 }}
              v-icon(v-else, small) {{ $vuetify.icons[dataset.row.labels[index]] }}
            td.px-2.row(
                v-for="(col, idx2) in row",
                :class="{[dataset.column.labels[idx2]]: true, 'active': isActive(idx2, 'column')}",
                :key="`${index}.${idx2}`") {{ col }}
</template>

<style lang="scss">
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
      border-radius: 4px;
      padding: 2px;
    }

    .radio-title {
      min-width: 110px;
    }

    .v-divider {
      height: 32px;
    }

    .radio-icon {
      padding: 2px;
      border-radius: 4px;
      margin: 4px;
    }
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
