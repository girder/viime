<template lang="pug">
table.cleanup-table(v-data-table="{ dataset, id, activeClasses, setSelection, selectedRanges }")
</template>

<script>
import { base26Converter } from '@/utils';


function updateTable(el, binding) {

  const { dataset, id, activeClasses, setSelection } = binding.value;
  const colLabels = dataset.column.labels;
  const rowLabels = dataset.row.labels;
  // const colgroup = el.getElementsByTagName('colgroup')[0];
  const head = el.getElementsByTagName('thead')[0];
  const body = el.getElementsByTagName('tbody')[0];
  // const columns = colgroup.children;
  const headers = head.children[0].children;  
  const rows = body.children;

  for(let index = 0; index < (headers.length - 1); index += 1) {
    const col = headers[index + 1]; // Account for 0th being empty
    col.classList.remove('first', 'last', 'active', 'key', 'group', 'metadata', 'masked', 'measurement');
    col.classList.add(...activeClasses(index, 'column'));
    col.classList.add(colLabels[index]);
  }


  for(let index = 0; index < (rows.length); index += 1) {
    const row = rows[index];
    row.classList.remove('first', 'last', 'active', 'header', 'metadata', 'masked', 'sample');
    row.classList.add(...activeClasses(index, 'row'));
    row.classList.add(rowLabels[index]);

    const columns = row.children;
    for(let index = 0; index < (columns.length - 1); index += 1) {
      const col = columns[index + 1];
      col.classList.remove('first', 'last', 'active', 'key', 'group', 'metadata', 'masked', 'measurement');
      col.classList.add(...activeClasses(index, 'column'));
      col.classList.add(colLabels[index]);
    }
  }
}

function renderTable(el, binding) {
  while(el.firstChild) {
    el.removeChild(el.firstChild);
  }

  const { dataset, id, activeClasses, setSelection } = binding.value;
  const thead = document.createElement('thead');
  // const colgroup = document.createElement('colgroup');
  const tr0 = document.createElement('tr');
  const th0 = document.createElement('th');
  const col0 = document.createElement('col');
  tr0.appendChild(th0);
  // colgroup.appendChild(col0);

  dataset.column.labels.forEach((col, index) => {
    // const coln = document.createElement('col');
    const thn = document.createElement('th');
    const span = document.createElement('span');
    span.innerText = base26Converter(index + 1);
    thn.onclick = (event) => {
      setSelection({ key: id, event, axis: 'column', idx: index });
    }
    thn.classList.add('control', 'px-2')
    // coln.classList.add(...activeClasses(index, 'column'));
    // coln.classList.add(dataset.column.labels[index]);
    thn.classList.add(...activeClasses(index, 'column'));
    
    thn.appendChild(span);
    tr0.appendChild(thn);
    // colgroup.appendChild(coln);
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
      tdn.classList.add(dataset.column.labels[idx2]);
      tdn.classList.add(...activeClasses(idx2, 'column'));
    });
  });

  // el.appendChild(colgroup);
  el.appendChild(thead);
  el.appendChild(tbody);
}

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    id: {
      type: String,
      required: true,
    },
    selected: {
      type: Object,
      required: true,
    },
  },
  directives: {
    dataTable: {
      inserted: renderTable,
      update: updateTable,
    }
  },
  computed: {
    selectedRanges() { return this.selected.ranges; },
    selectedType() { return this.selected.type; },
  },
  methods: {
    activeClasses(index, axisName) {
      if (axisName === this.selected.type) {
        const ranges = this.selectedRanges;
        const includes = ranges.includes(index);
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
    setSelection(selection) {
      this.$emit('setSelection', selection);
    },
  },
}
</script>

<style lang="scss">
@mixin masked() {
  background-color: var(--v-secondary-lighten3);
  box-shadow: inset 0 0 0 .5px var(--v-secondary-lighten2);
  font-weight: 300;
  color: var(--v-secondary-base);
}

.cleanup-table {
  border-spacing: 0px;
  user-select: none;

  .key, .metadata, .header, .group {
    color: white;
    font-weight: 700;
    text-align: left;
  }

  tr {
    background-color: #fdfdfd;

    th, td {
      box-shadow: inset 0 0 0 .5px var(--v-secondary-lighten3);
      padding: 2px;
      text-align: center;
      white-space: nowrap;

      &.control {
        cursor: pointer;
        font-weight: 300;
      }
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

    &.active {
      &.metadata {
        td {
          box-shadow: inset 0 0 0 .5px rgba(161, 213, 255, 0.15) !important;
        }
      }
    }

    &.active td,
    td.active {
      background: linear-gradient(0deg,rgba(161, 213, 255, 0.2),rgba(161, 213, 255, 0.2));
      box-shadow: inset 0 0 0 .5px rgba(161, 213, 255, 0.3);

      &.group,
      &.key,
      &.metadata,
      &.masked {
        box-shadow: inset 0 0 0 .5px rgba(161, 213, 255, 0.15) !important;
      }
    }
  }

  tr.datarow {
    &.header {
      td {
        background-color: var(--v-accent-lighten1);
        box-shadow: inset 0 0 0 .5px var(--v-accent-base);

        &.active {
          color: white;

          &.first{
            // border-left: 2px solid var(--v-secondary-darken3);
          }
          &.last {
            // border-right: 2px solid var(--v-secondary-darken3);
          }
        }
        &.masked {
          color: var(--v-secondary-base);
        }
      }
    }

    &.metadata {
      td {
        background-color: var(--v-accent2-lighten2);
        box-shadow: inset 0 0 0 .5px var(--v-accent2-lighten1);
      }
    }

    &.header,
    &.metadata {
      td.key, td.metadata, td.group {
        @include masked();
      }
    }

    td {
      &.key {
        background-color: var(--v-primary-base);
        box-shadow: inset 0 0 0 .5px var(--v-primary-darken1);
      }

      &.metadata, {
        background-color: var(--v-accent2-lighten2);
        box-shadow: inset 0 0 0 .5px var(--v-accent2-lighten1);
      }

      &.group {
        background-color: var(--v-accent3-lighten1);
        box-shadow: inset 0 0 0 .5px var(--v-accent3-base);
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
</style>