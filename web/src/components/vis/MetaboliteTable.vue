<script>
import { format } from 'd3-format';

export default {

  props: {
    items: {
      type: Array,
      required: true,
    },
    value: {
      type: Array,
      required: true,
    },
    headers: {
      type: Array,
      required: true,
    },
    threshold: {
      type: Number,
      required: false,
      default: 0.05,
    },
  },

  data() {
    const filters = {};
    this.headers.forEach((header) => {
      filters[header.value] = Infinity;
    });
    return {
      format: format('.4e'),
      pagination: {
        rowsPerPage: -1,
      },
      // need to use this workaround, since `header-cell` as slot name doesn't work
      // and `headerCell` isn't allowed by the linter
      headercell: 'headerCell',
      filters,
    };
  },

  computed: {
    selectedItems: {
      get() {
        const s = new Set(this.value);
        return this.items.filter(d => s.has(d.Metabolite));
      },
      set(newValue) {
        const s = newValue.map(d => d.Metabolite);
        this.$emit('input', s);
      },
    },
    filteredItems() {
      const filters = Object.entries(this.filters).filter(entry => entry[1] < 0.1);
      if (filters.length === 0) {
        return this.items;
      }
      return this.items.filter(item => filters.every(([k, v]) => item[k] <= v));
    },
  },

  methods: {
    isInteresting(value) {
      return value < this.threshold;
    },
    setFilter(header, value) {
      this.filters[header.value] = value === 0.1 ? Infinity : value;
    },
  },
};
</script>

<template lang="pug">
v-data-table.elevation-1.main(:headers="headers", :items="filteredItems", disable-initial-sort,
    item-key="Metabolite", :pagination.sync="pagination",
    v-model="selectedItems", select-all)
  template(v-slot:[headercell]="{header}")
    | {{header.text}}
    v-slider(v-if="header.filter", min="0", max="0.1", step="0.001", thumb-label,
        :title="`Filter ${header.text} <= ${filters[header.value]}`",
        :value="filters[header.value]", @input="setFilter(header, $event)",
        hide-details, @click="$event.stopPropagation()")
  template(#items="props")
    td.cell
      v-checkbox(v-model="props.selected", hide-details)
    td.cell {{ props.item.Metabolite }}
    td.cell.text-xs-right(v-for="c in headers.slice(1)",
        :class="isInteresting(props.item[c.value]) ? 'highlight' : ''")
      | {{ format(props.item[c.value]) }}
</template>

<style scoped>
.highlight {
  background-color: #ffadad;
}

.main {
  height: 0;
}

.main >>> table {
  width: unset;
}

.main >>> tr {
  height: 25px;
}
.main >>> td.cell,
.main >>> thead > tr > th {
  height: 25px;
  padding: 2px 7px;
}

.main >>> thead > tr > th {
  position: relative;
  height: 50px;
  vertical-align: top;
}

.main >>> thead > tr > th:nth-child(2) {
  min-width: 20em;
}

.v-input--slider {
  position: absolute;
  bottom: 0;
  padding: 2px 2px;
  box-sizing: border-box;
  margin: 0;
  width: unset;
}

.v-input--slider >>> .v-slider__thumb-label {
  top: 100%;
  border-radius: 0 50% 50%;
  bottom: unset;
  transform: translateY(20%) translateY(12px) translateX(-50%) rotate(45deg);
}
</style>
