<template lang="pug">
table.cleanup-table(v-data-table="bind", :key="id")
</template>

<script>
import { base26Converter } from '@/utils';
import {
  defaultRowOption,
  defaultColOption,
} from '@/utils/constants';

function getIcon(iconType, icons) {
  const el = document.createElement('i');
  el.classList.add(...['v-icon', 'small', 'mdi', 'theme--light', icons[iconType]]);
  el.style.fontSize = '16px';
  return el;
}

function updateTable(el, binding) {
  const {
    dataset, activeClasses, icons,
  } = binding.value;
  const colgroup = el.getElementsByTagName('colgroup')[0];
  const body = el.getElementsByTagName('tbody')[0];
  const headrow = el.getElementsByTagName('thead')[0].children[0];
  const columns = colgroup.children;
  const rows = body.children;
  for (let index = 0; index < columns.length - 1; index += 1) {
    const col = columns[index + 1]; // Account for 0th being empty
    col.classList.remove(
      'first',
      'last',
      'active',
      'key',
      'group',
      'metadata',
      'masked',
      'measurement',
    );
    col.classList.add(...activeClasses(index, 'column'));
    const colType = dataset.column.labels[index];
    col.classList.add(colType);

    const colHeader = headrow.children[index + 1];
    colHeader.removeChild(colHeader.firstChild);
    if (colType !== defaultColOption) {
      colHeader.appendChild(getIcon(colType, icons));
    } else {
      colHeader.innerText = base26Converter(index + 1);
    }
  }

  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index];
    row.classList.remove(
      'first',
      'last',
      'active',
      'header',
      'metadata',
      'masked',
      'sample',
    );
    row.classList.add(...activeClasses(index, 'row'));
    const rowType = dataset.row.labels[index];
    row.classList.add(rowType);

    const rowHeader = row.children[0];
    rowHeader.removeChild(rowHeader.firstChild);
    if (rowType !== defaultRowOption) {
      rowHeader.appendChild(getIcon(rowType, icons));
    } else {
      rowHeader.innerText = index + 1;
    }
  }
}

function renderTable(el, binding) {
  while (el.firstChild) {
    el.removeChild(el.firstChild);
  }
  const {
    dataset, id, activeClasses, setSelection, icons,
  } = binding.value;
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
    const colType = dataset.column.labels[index];
    thn.onclick = (event) => {
      setSelection({
        key: id, event, axis: 'column', idx: index,
      });
    };
    if (colType !== defaultColOption) {
      span.appendChild(getIcon(colType, icons));
    } else {
      span.innerText = base26Converter(index + 1);
    }
    thn.classList.add('control', 'px-2', `column-key-${index}`);
    coln.classList.add(...activeClasses(index, 'column'));
    coln.classList.add(colType);
    thn.appendChild(span);
    tr0.appendChild(thn);
    colgroup.appendChild(coln);
  });
  thead.appendChild(tr0);

  const tbody = document.createElement('tbody');
  dataset.sourcerows.forEach((row, index) => {
    const trn = document.createElement('tr');
    const rowType = dataset.row.labels[index];
    trn.classList.add(...['datarow'].concat(activeClasses(index, 'row')));
    trn.classList.add(rowType);
    tbody.appendChild(trn);
    const td = document.createElement('td');
    if (rowType !== defaultRowOption) {
      td.appendChild(getIcon(rowType, icons));
    } else {
      td.innerText = index + 1;
    }
    td.classList.add('control', `row-key-${index}`);
    td.onclick = (event) => {
      setSelection({
        key: id, event, axis: 'row', idx: index,
      });
    };
    trn.appendChild(td);
    row.forEach((col) => {
      const tdn = document.createElement('td');
      tdn.innerText = col;
      trn.appendChild(tdn);
      tdn.classList.add('row');
    });
  });
  el.classList.add(dataset.id);
  el.appendChild(colgroup);
  el.appendChild(thead);
  el.appendChild(tbody);
}

export default {
  directives: {
    dataTable: {
      inserted: renderTable,
      update: updateTable,
    },
  },
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
  computed: {
    selectedRanges() {
      return this.selected.ranges;
    },
    selectedType() {
      return this.selected.type;
    },
    bind() {
      const {
        dataset, id, activeClasses, setSelection, selectedRanges,
      } = this;
      const { icons } = this.$vuetify;
      return {
        dataset, id, activeClasses, setSelection, selectedRanges, icons,
      };
    },
  },
  watch: {
    selectedRanges(val) {
      this.scrollIntoView(this.selectedType, val.members[0]);
    },
    selectedType(val) {
      this.scrollIntoView(val, this.selectedRanges.members[0]);
    },
  },
  methods: {
    scrollIntoView(type, index) {
      const table = document.getElementsByClassName(this.id)[0];
      const cell = table.getElementsByClassName(`${type}-key-${index}`)[0];
      cell.scrollIntoView({block: 'nearest', inline: 'nearest', behavior: 'auto' });
    },
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
      this.$emit('setselection', selection);
    },
  },
};
</script>

<style lang="scss">
@mixin masked() {
  background-color: var(--v-secondary-lighten2);
  font-weight: 300;
  color: var(--v-secondary-base);
}

.cleanup-table {
  border-spacing: 0px;
  user-select: none;
  table-layout: fixed;
  border-collapse: collapse;

  .key,
  .metadata,
  .header,
  .group {
    color: white;
    font-weight: 700;
    text-align: left;
  }

  colgroup {
    col {
      &.active {
        background: linear-gradient(
          0deg,
          rgba(161, 213, 255, 0.4),
          rgba(161, 213, 255, 0.4)
        );

        &.first {
          background: linear-gradient(
            90deg,
            rgb(23, 147, 248) 0px,
            rgba(161, 213, 255, 0.4) 2px
          );
        }

        &.last {
          background: linear-gradient(
            90deg,
            rgba(161, 213, 255, 0.4) 0px,
            rgba(161, 213, 255, 0.4) calc(100% - 2px),
            rgb(23, 147, 248) 100%
          );
        }

        &.first.last {
          background: linear-gradient(
            90deg,
            rgb(23, 147, 248) 0px,
            rgba(161, 213, 255, 0.4) 2px,
            rgba(161, 213, 255, 0.4) calc(100% - 2px),
            rgb(23, 147, 248) 100%
          );
        }
      }

      &.active.key,
      &.key,
      &.active.first.key,
      &.active.last.key {
        background-color: var(--v-primary-lighten3);
      }

      &.active.metadata,
      &.metadata,
      &.active.first.metadata,
      &.active.last.metadata {
        background-color: var(--v-accent2-lighten3);
      }

      &.active.group,
      &.group,
      &.active.first.group,
      &.active.last.group {
        background-color: var(--v-accent3-lighten3);
      }

      &.masked,
      &.masked.active,
      &.masked.active.first,
      &.masked.active.last {
        @include masked();
      }
    }
  }

  tr {
    th,
    td {
      padding: 2px 7px;
      white-space: nowrap;

      &.control {
        cursor: pointer;
        font-weight: 300;
      }
    }

    &.active {
      &.metadata {
        td {
          box-shadow: inset 0 0 0 0.5px rgba(161, 213, 255, 0.15) !important;
        }
      }
    }

    &.active {
      background: linear-gradient(
        0deg,
        rgba(161, 213, 255, 0.4),
        rgba(161, 213, 255, 0.4)
      );

      &.first {
        background: linear-gradient(
          180deg,
          rgb(23, 147, 248) 0px,
          rgba(161, 213, 255, 0.4) 2px
        );
      }

      &.last {
        background: linear-gradient(
          180deg,
          rgba(161, 213, 255, 0.4) 0px,
          rgba(161, 213, 255, 0.4) calc(100% - 2px),
          rgb(23, 147, 248) 100%
        );
      }

      &.first.last {
        background: linear-gradient(
          180deg,
          rgb(23, 147, 248) 0px,
          rgba(161, 213, 255, 0.4) 2px,
          rgba(161, 213, 255, 0.4) calc(100% - 2px),
          rgb(23, 147, 248) 100%
        );
      }
    }
  }

  tr.datarow {
    text-align: left;

    &.header,
    &.header.active {
      background-color: var(--v-accent-lighten1);
    }

    &.metadata,
    &.metadata.active {
      background-color: var(--v-accent2-lighten2);
    }
  }

  tr.datarow {
    &.masked,
    &.masked.active {
      @include masked();
    }
  }
}
</style>
