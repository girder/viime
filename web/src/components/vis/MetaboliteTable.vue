<script>
import { format } from 'd3-format';
import { colors } from '../../utils/constants';
import { textColor } from '../../utils';

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
      default: 0.05,
    },
    noDataAvailableMsg: { // allows displaying a custom message when table has no data.
      type: String,
      default: 'No data available',
    },
  },

  data() {
    return {
      format: format('.4e'),
      pagination: {
        rowsPerPage: -1,
      },
      // need to use this workaround, since `header-cell` as slot name doesn't work
      // and `headerCell` isn't allowed by the linter
      headercell: 'headerCell',
      colors,
    };
  },

  computed: {
    selectedItems: {
      get() {
        const s = new Set(this.value);
        return this.items.filter((d) => s.has(d.Metabolite));
      },
      set(newValue) {
        const s = newValue.map((d) => d.Metabolite);
        this.$emit('input', s);
      },
    },
  },

  methods: {
    isInteresting(value) {
      return value < this.threshold;
    },
    toggleHighlighted(header, evt, add) {
      evt.preventDefault();
      evt.stopPropagation();

      const highlighted = this.items.filter((item) => this.isInteresting(item[header.value]));
      const current = this.selectedItems.slice();
      const currentLookup = new Set(current);
      highlighted.forEach((item) => {
        if (add && !currentLookup.has(item)) {
          current.push(item);
        } else if (!add && currentLookup.has(item)) {
          const index = current.indexOf(item);
          current.splice(index, 1);
        }
      });
      this.selectedItems = current;
    },
    cellStyle(item) {
      if (!item.color) {
        return null;
      }
      return {
        backgroundColor: item.color,
        color: textColor(item.color),
      };
    },
  },
};
</script>

<template lang="pug">
v-data-table.elevation-1.main(:headers="headers", :items="items", disable-initial-sort,
    item-key="Metabolite", :pagination.sync="pagination",
    v-model="selectedItems", select-all)
  template(v-slot:[headercell]="{header}")
    | {{header.text}}
    v-btn.toggle(icon, small, @click="toggleHighlighted(header, $event, true)",
        title="Adds the highlighted Metabolites to the selected set",
        v-if="!header.isLabel")
      span.mdi(:class="{ [$vuetify.icons.plusMultiple]: true }")
    v-btn.toggle(icon, small, @click="toggleHighlighted(header, $event, false)",
        title="Removes the highlighted Metabolites from the selected set",
        v-if="!header.isLabel")
      span.mdi(:class="{ [$vuetify.icons.minusMultiple]: true }")

  template(#items="props")
    td.cell
      v-checkbox(v-model="props.selected", hide-details, :color="colors.selected")
    td.cell(:style="cellStyle(props.item)") {{ props.item.Metabolite }}
    td.cell.text-xs-right(v-for="c in headers.slice(1)",
        :class="isInteresting(props.item[c.value]) ? 'highlight' : ''")
      | {{ format(props.item[c.value]) }}
  template(slot="no-data")
    | {{ noDataAvailableMsg }}
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

.toggle {
  margin: 0;
  opacity: 0;
}

.main >>> thead > tr > th:hover .toggle {
  opacity: 0.6;
}

</style>
