<script>
import AnalyzeBaseVue from './AnalyzeBase.vue';
import {wilcoxon_zero_methods, wilcoxon_alternatives} from '../../utils/constants';
import {scaleSequential} from 'd3-scale';
import {interpolateGreys} from 'd3-scale-chromatic';
import {format} from 'd3-format';

export default {
  extends: AnalyzeBaseVue,
  components: {
  },
  props: {
    
  },
  data() {
    return {
      key: 'wilcoxon',
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
  computed: {
    scale() {
      const max_p_value = this.results ? this.results.data.reduce((acc, entry) => Math.max(acc, entry.p), 0) : 1;
      return scaleSequential(interpolateGreys).domain([max_p_value, 0]);
    },
    indices() { return this.results ? this.results.indices : []},
    resultLookup() {
      if (!this.results) {
        return new Map();
      }
      const scale = this.scale;
      const f = format('.2e');
      const r = new Map();
      this.results.data.forEach((entry) => {
        const {x, y} = entry;
        const key = this.computeKey(x, y);
        entry.color = scale(entry.p);
        entry.title = `${entry.x} / ${entry.y} : p-value: ${f(entry.p)} score: ${f(entry.score)}`;
        r.set(key, entry);
      });
      return r;
    }
  },
  watch: {
  },
  methods: {
    computeKey(i, j) {
      if (j < i) {
        // swap to have a clear name
        const s = i;
        i = j;
        j = s;
      }
      return `${i}#${j}`;
    },
    getCell(x, y) {
      const key = this.computeKey(x, y);
      if (!this.resultLookup.has(key)) {
        if (x === y) {
          // center
          return {x, y, p: '', score: NaN, color: null};  
        }
        return {x, y, p: NaN, score: NaN, color: null};
      }
      return this.resultLookup.get(key);
    },
    getRow(x) {
      return this.indices.map((y) => this.getCell(x, y));
    }
  },
};
</script>

<template lang="pug">
extends AnalyzeBase.pug

block toolbar
  v-navigation-drawer.primary.darken-3(permanent, style="width: 200px; min-width: 200px;")
    v-layout(column, fill-height, v-if="dataset && ready")
      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Zero Methods
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="options.zero_method",
              hide-details,
              @change="changeOption({zero_method: $event})",)
            v-radio(v-for="m in zero_methods", :label="m.label",
                :value="m.value", :key="`zero${m.value}`")
      v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
        v-toolbar-title Alternatives
      v-card.mx-3(flat)
        v-card-actions
          v-radio-group.my-0(:value="options.alternative",
              hide-details,
              @change="changeOption({alternative: $event})",)
            v-radio(v-for="m in alternatives", :label="m.label",
                :value="m.value", :key="`alt${m.value}`")
      v-btn(
        @click="compute()")
        | Analyze

block content
  table
    thead
      tr
        th
        th(v-for="(y,i) in indices", :key="i", v-text="y", :title="y")
    tbody
      tr(v-for="(x,i) in indices", :key="i")
        th(v-text="x", :title="x")
        td(v-for="(cell,j) in getRow(x)", :key="j", :style="{backgroundColor: cell.color}", :title="cell.title")
  
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
