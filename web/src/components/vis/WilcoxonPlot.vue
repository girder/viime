<script>
import { scaleSequential } from 'd3-scale';
import { interpolateGreys } from 'd3-scale-chromatic';
import { format } from 'd3-format';
import Vue from 'vue';

export default {
  props: {
    data: {
      required: true,
      validator: prop => !prop || ('data' in prop && 'indices' in prop),
    },
  },

  computed: {
    entries() { return (this.data && this.data.data) || []; },
    indices() { return (this.data && this.data.indices) || []; },
    scale() {
      const max_p_value = this.entries.reduce(
        (acc, entry) => Math.max(acc, entry.p), 0,
      ) || 1;
      return scaleSequential(interpolateGreys).domain([max_p_value, 0]);
    },
    resultLookup() {
      const f = format('.2e');
      const r = new Map();
      this.entries.forEach((entry) => {
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
table.heatmap
  thead
    tr
      th
      th.cell(v-for="(y,i) in indices", :key="i", v-text="y", :title="y")
  tbody
    tr(v-for="(x,i) in indices", :key="i")
      th.heatmaplabel(v-text="x", :title="x")
      td.cell(v-for="(cell,j) in getRow(x)",
          :key="j",
          :style="{ backgroundColor: cell.color }", :title="cell.title")
</template>

<style lang="scss" scoped>
  .heatmap {
    table-layout: fixed;
  }

  .cell {
    max-width: 3em;
    width: 3em;
    min-width: 3em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .heatmaplabel {
    text-align: left;
  }
</style>
