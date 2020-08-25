<script lang="ts">
import {
  PropType, defineComponent, computed, reactive, ref,
} from '@vue/composition-api';
import { format as d3Format } from 'd3-format';
import { colors } from '../../utils/constants';
import { textColor } from '../../utils';

export interface Item {
  Metabolite: string;
  color: string;
  [key: string]: number | string;
}

interface Header {
  text: string;
  align?: string;
  value: string;
  isLabel: boolean;
}

export default defineComponent({
  props: {
    items: {
      type: Array as PropType<Item[]>,
      required: true,
    },
    value: {
      type: Array as PropType<string[]>,
      required: true,
    },
    headers: {
      type: Array as PropType<Header[]>,
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

  setup(props, { emit }) {
    const format = ref(d3Format('.4e'));
    const pagination = reactive({ rowsPerPage: -1 });
    const selectedItems = computed<Item[]>({
      get() {
        const s = new Set(props.value);
        return props.items.filter((d) => s.has(d.Metabolite));
      },
      set(newValue) {
        const s = newValue.map((d) => d.Metabolite);
        emit('input', s);
      },
    });

    function isInteresting(value: number) {
      return value < props.threshold;
    }
    function toggleHighlighted(header: Header, evt: Event, add: boolean) {
      evt.preventDefault();
      evt.stopPropagation();

      const highlighted = props.items.filter((item) => isInteresting(item[header.value] as number));
      const current = selectedItems.value.slice();
      const currentLookup = new Set(current);
      highlighted.forEach((item) => {
        if (add && !currentLookup.has(item)) {
          current.push(item);
        } else if (!add && currentLookup.has(item)) {
          const index = current.indexOf(item);
          current.splice(index, 1);
        }
      });
      selectedItems.value = current;
    }
    function cellStyle(item: Item) {
      if (!item.color) {
        return null;
      }
      return {
        backgroundColor: item.color,
        color: textColor(item.color),
      };
    }
    return {
      format,
      pagination,
      colors,
      selectedItems,
      isInteresting,
      toggleHighlighted,
      cellStyle,
    };
  },
});
</script>

<template>
  <v-data-table
    v-model="selectedItems"
    class="elevation-1 main"
    :headers="headers"
    :items="items"
    disable-initial-sort="disable-initial-sort"
    item-key="Metabolite"
    :pagination.sync="pagination"
    select-all="select-all"
  >
    <template v-slot:headerCell="{ header }">
      {{ header.text }}<v-btn
        v-if="!header.isLabel"
        class="toggle"
        icon="icon"
        small="small"
        title="Adds the highlighted Metabolites to the selected set"
        @click="toggleHighlighted(header, $event, true)"
      >
        <span
          class="mdi"
          :class="{ [$vuetify.icons.plusMultiple]: true }"
        />
      </v-btn>
      <v-btn
        v-if="!header.isLabel"
        class="toggle"
        icon="icon"
        small="small"
        title="Removes the highlighted Metabolites from the selected set"
        @click="toggleHighlighted(header, $event, false)"
      >
        <span
          class="mdi"
          :class="{ [$vuetify.icons.minusMultiple]: true }"
        />
      </v-btn>
    </template>
    <template #items="props">
      <td class="cell">
        <v-checkbox
          v-model="props.selected"
          hide-details="hide-details"
          :color="colors.selected"
        />
      </td>
      <td
        class="cell"
        :style="cellStyle(props.item)"
      >
        {{ props.item.Metabolite }}
      </td>
      <td
        v-for="c in headers.slice(1)"
        :key="c.value"
        class="cell text-xs-right"
        :class="isInteresting(props.item[c.value]) ? 'highlight' : ''"
      >
        {{ format(props.item[c.value]) }}
      </td>
    </template>
    <template slot="no-data">
      {{ noDataAvailableMsg }}
    </template>
  </v-data-table>
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
