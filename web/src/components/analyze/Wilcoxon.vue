<script>
import { scaleSequential } from 'd3-scale';
import { interpolateGreys } from 'd3-scale-chromatic';
import { format } from 'd3-format';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';
import { analyzeMixin } from './mixins';

export default {
  mixins: [analyzeMixin('wilcoxon')],
  data() {
    return {
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
  computed: {
    scale() {
      const max_p_value = this.results ? this.results.data.reduce(
        (acc, entry) => Math.max(acc, entry.p), 0,
      ) : 1;
      return scaleSequential(interpolateGreys).domain([max_p_value, 0]);
    },
    indices() { return this.results ? this.results.indices : []; },
    resultLookup() {
      if (!this.results) {
        return new Map();
      }
      const f = format('.2e');
      const r = new Map();
      this.results.data.forEach((entry) => {
        const { x, y } = entry;
        const key = this.computeKey(x, y);
        entry.color = this.scale(entry.p);
        entry.title = `${entry.x} / ${entry.y} : p-value: ${f(entry.p)} score: ${f(entry.score)}`;
        r.set(key, entry);
      });
      return r;
    },
  },
  methods: {
    computeKey(i, j) {
      return j < i ? `${j}#${i}` : `${i}#${j}`;
    },
    getCell(x, y) {
      const key = this.computeKey(x, y);
      if (!this.resultLookup.has(key)) {
        if (x === y) {
          // center
          return {
            x, y, p: '', score: NaN, color: null,
          };
        }
        return {
          x, y, p: NaN, score: NaN, color: null,
        };
      }
      return this.resultLookup.get(key);
    },
    getRow(x) {
      return this.indices.map(y => this.getCell(x, y));
    },
  },
};
</script>

<template lang="pug">
analyze-wrapper(:id="id", :name="name")
  template(v-slot:toolbar)
    toolbar-option(title="Zero Methods", :value="options.zero_method",
        :options="zero_methods",
        @change="changeOption({zero_method: $event})")
    toolbar-option(title="Alternatives", :value="options.alternative",
        :options="alternatives",
        @change="changeOption({alternative: $event})")

  table
    thead
      tr
        th
        th(v-for="(y,i) in indices", :key="i", v-text="y", :title="y")
    tbody
      tr(v-for="(x,i) in indices", :key="i")
        th(v-text="x", :title="x")
        td(v-for="(cell,j) in getRow(x)",
            :key="j",
            :style="{backgroundColor: cell.color}", :title="cell.title")
</template>

<style scoped lang="scss">
  table {
    table-layout: fixed;
  }

  thead th,
  td {
    max-width: 3em;
    width: 3em;
    min-width: 3em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  tbody th {
    text-align: left;
  }
</style>
