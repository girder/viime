<script>
import { mapMutations } from 'vuex';
import { CHANGE_AXIS_LABEL, CHANGE_IMPUTATION_OPTIONS } from '@/store/actions.type';
import { SET_SELECTION } from '@/store/mutations.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
  mcar_imputation_methods,
  mnar_imputation_methods,
} from '@/utils/constants';
import { base26Converter } from '@/utils';
import SaveStatus from '@/components/SaveStatus.vue';

function updateTable(el, binding) {
  const { dataset, id, activeClasses, setSelection } = binding.value;
  const colgroup = el.getElementsByTagName('colgroup')[0];
  const body = el.getElementsByTagName('tbody')[0];
  const columns = colgroup.children;
  const rows = body.children;
  for(let index = 0; index < (columns.length - 1); index += 1) {
    const col = columns[index + 1]; // Account for 0th being empty
    col.classList.remove('first', 'last', 'active', 'key', 'group', 'metadata', 'masked', 'measurement');
    col.classList.add(...activeClasses(index, 'column'));
    col.classList.add(dataset.column.labels[index]);
  }

  for(let index = 0; index < (rows.length); index += 1) {
    const row = rows[index];
    row.classList.remove('first', 'last', 'active', 'header', 'metadata', 'masked', 'sample');
    row.classList.add(...activeClasses(index, 'row'));
    row.classList.add(dataset.row.labels[index]);
  }
}

function renderTable(el, binding) {
  while(el.firstChild) {
    el.removeChild(el.firstChild);
  }

  const { dataset, id, activeClasses, setSelection } = binding.value;
  const thead = document.createElement('thead');
  const colgroup = document.createElement('colgroup');
  const tr0 = document.createElement('tr');
  const th0 = document.createElement('th');
  const col0 = document.createElement('col');
  tr0.appendChild(th0);
  colgroup.appendChild(col0);

  dataset.column.labels.forEach((col, index) => {
    const coln = document.createElement('col');
    const thn = document.createElement('th');
    const span = document.createElement('span');
    span.innerText = base26Converter(index + 1);
    thn.onclick = (event) => {
      setSelection({ key: id, event, axis: 'column', idx: index });
    }
    thn.classList.add('control', 'px-2')
    coln.classList.add(...activeClasses(index, 'column'));
    coln.classList.add(dataset.column.labels[index]);
    thn.appendChild(span);
    tr0.appendChild(thn);
    colgroup.appendChild(coln);
  });
  thead.appendChild(tr0);
  
  const tbody = document.createElement('tbody');
  dataset.sourcerows.forEach((row, index) => {
    const trn = document.createElement('tr');
    trn.classList.add(...['datarow'].concat(activeClasses(index, 'row')));
    trn.classList.add(dataset.row.labels[index]);
    tbody.appendChild(trn);
    const td = document.createElement('td');
    td.innerText = index + 1;
    td.classList.add('control');
    td.onclick = (event) => {
      setSelection({ key: id, event, axis: 'row', idx: index });
    }
    trn.appendChild(td);
    row.forEach((col, idx2) => {
      const tdn = document.createElement('td');
      tdn.innerText = col;
      trn.appendChild(tdn);
      tdn.classList.add('row');
    });
  });

  el.appendChild(colgroup);
  el.appendChild(thead);
  el.appendChild(tbody);
}

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
      settingsDialog: false,
      mnarImputationMethods: mnar_imputation_methods,
      mcarImputationMethods: mcar_imputation_methods,
      imputation: {},
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
  },
  watch: {
    dataset() {
      this.imputation.mnar = this.dataset.imputationMNAR;
      this.imputation.mcar = this.dataset.imputationMCAR;
    },
  },
  directives: {
    dataTable: {
      inserted: renderTable,
      update: updateTable,
    }
  },
  methods: {
    ...mapMutations({ setSelection: SET_SELECTION }),
    base26Converter,
    async selectOption(label) {
      const { ranges, type: context } = this.selected;
      const changes = ranges.members.map(index => ({ context, index, label }));
      await this.$store.dispatch(CHANGE_AXIS_LABEL, { dataset_id: this.id, changes });
    },
    async saveImputationSettings() {
      this.settingsDialog = false;
      await this.$store.dispatch(CHANGE_IMPUTATION_OPTIONS, {
        dataset_id: this.id,
        options: this.imputation,
      });
    },
    activeClasses(index, axisName) {
      if (axisName === this.selected.type) {
        const includes = this.selected.ranges.includes(index);
        const classList = [];
        if (includes.member) {
          classList.push('active');
        }
        if (includes.first) {
          classList.push('first');
        }
        if (includes.last) {
          classList.push('last');
        }
        return classList;
      }
      return [];
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
      v-dialog(v-model="settingsDialog", max-width="500")
        template(v-slot:activator="{ on }")
          v-btn(icon, v-on="on")
            v-icon {{ $vuetify.icons.settings }}
        v-card
          v-card-title.headline Imputation Settings
          v-card-text
            v-select(
                item-value="value",
                item-text="label",
                :items="mnarImputationMethods",
                label="MNAR imputation method",
                v-model="imputation.mnar")
            v-select(
                item-value="value",
                item-text="label",
                :items="mcarImputationMethods",
                label="MCAR imputation method",
                v-model="imputation.mcar")
          v-card-actions
            v-spacer
            v-btn(flat, @click="settingsDialog = false") Close
            v-btn(flat, @click="saveImputationSettings") Save
      v-icon {{ $vuetify.icons.download }}

    .overflow-auto
      table.cleanup-table(v-data-table="this")
</template>

<style lang="scss">
@mixin masked() {
  background-color: var(--v-secondary-lighten3);
  box-shadow: inset 0 0 0 .5px var(--v-secondary-lighten2);
  font-weight: 300;
  color: var(--v-secondary-base);
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
    table-layout: fixed;
    border-collapse: collapse;

    .key, .metadata, .header, .group {
      color: white;
      font-weight: 700;
      text-align: left;
    }
    
    colgroup {
      col {
        &.active {
          background: linear-gradient(0deg,rgba(161, 213, 255, 0.3),rgba(161, 213, 255, 0.3));
          border-left-color: red !important;
        }

        &.active.key, &.key {
          background-color:  var(--v-primary-lighten4);
        }

        &.active.metadata, &.metadata {
          background-color:  var(--v-accent2-lighten3);
        }

        &.active.group, &.group {
          background-color:   var(--v-accent3-lighten3);
        }
      }
    }

    tr {

      th, td {
        // border: 1px solid var(--v-secondary-lighten1);
        padding: 2px 5px;
        text-align: center;
        white-space: nowrap;

        &.control {
          cursor: pointer;
          font-weight: 300;
        }
      }

      &.active td {
        background: linear-gradient(0deg,rgba(161, 213, 255, 0.3),rgba(161, 213, 255, 0.3));

        &.group,
        &.key,
        &.metadata,
        &.masked {
          // box-shadow: inset 0 0 0 .5px rgba(161, 213, 255, 0.15) !important;
        }
      }
    }

    tr.datarow {
      
      &.header {
        td {
          background-color: var(--v-accent-lighten1);
        }
      }

      &.metadata {
        td {
          background-color: var(--v-accent2-lighten2);
          // box-shadow: inset 0 0 0 .5px var(--v-accent2-lighten1);
        }
      }

      &.header,
      &.metadata {
        td.key, td.metadata, td.group {
          @include masked();
        }
      }
    }

    tr.datarow {
      &.masked td,
      td.masked,
      th.masked {
        @include masked();
      }
    }
  }
}

</style>
