<script>
import resize from 'vue-resize-directive';
import { format } from 'd3-format';
import { hierarchy, cluster } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateRdBu, schemeRdBu } from 'd3-scale-chromatic';
import { select, event } from 'd3-selection';
import { svg2url } from '../../utils/exporter';

function domain(arr) {
  // let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  arr.forEach((row) => row.forEach((v) => {
    // if (v < min) {
    //   min = v;
    // }
    // if (v > max) {
    //   max = v;
    // }
    const av = Math.abs(v);
    if (av > max) {
      max = av;
    }
  }));
  return [-max, max];
  // return [min, max];
}

function aggregate(arr, rs, cs, transposed) {
  let is = rs;
  let js = cs;

  if (transposed) {
    is = cs;
    js = rs;
  }

  if (is.length === 1 && js.length === 1) {
    return arr[is[0]][js[0]];
  }
  // average
  const l = is.length * js.length;
  const sum = is.reduce((acc, i) => acc + js.reduce((acc2, j) => acc2 + arr[i][j], 0), 0);
  return sum / l;
}

const DENDROGRAM_RATIO = 0.2;
const LABEL_WIDTH = 150;

const MDI_PLUS_CIRCLE = '\uF417;';
const MDI_MINUS_CIRCLE = '\uF376;';
const MDI_STAR_CIRCLE = '\uF4CF;';

// max font size in px for metabolite names.
// Anything larger will cause metabolite
// names to be misaligned
const MAX_FONT_SIZE = 12;

export const heatmapLayouts = [
  { label: 'Auto', value: 'auto' },
  { label: 'Full', value: 'full' },
  { label: 'Square Cells', value: 'squareCells' },
  { label: 'Square Matrix', value: 'squareMatrix' },
];

/**
 * changes the `wrapper.hovered` value to a set of the given `arr` if needed
 * if needed ... if the value is different than the current value
 * this will avoid  unnecessary updates since Vue cannot handle Sets natively
 *
 * @param {{hovered: Set<T>}} wrapper wrapper object to update
 * @param {T[] | null} arr values to set
 * @returns {boolean} whether the value has changed
 */
function changeHovered(wrapper, arr) {
  if (!arr) {
    if (wrapper.hovered.size > 0) {
      wrapper.hovered = new Set();
      return true;
    }
    return false;
  }

  const old = wrapper.hovered;

  if (old.size !== arr.length) {
    wrapper.hovered = new Set(arr);
    return true;
  }
  if (old.size === 0 || ((arr.length === 1 && old.has(arr[0])) || arr.every((d) => old.has(d)))) {
    return false;
  }

  wrapper.hovered = new Set(arr);
  return true;
}

export default {
  directives: {
    resize,
  },
  props: {
    values: { // number[][]
      type: Array,
      default: () => [],
    },
    original: { // { columns: string[], rows: string[], values: number[][] }
      type: Object,
      default: () => {},
    },
    columnClustering: { // ITreeNode
      type: Object,
      default: null,
    },
    rowClustering: { // ITreeNode
      type: Object,
      default: null,
    },
    rowConfig: { // { dendrogram: boolean, colorer?: (name) => string }
      type: Object,
      default: () => ({ dendrogram: true, colorer: null }),
    },
    columnConfig: { // { dendrogram: boolean, colorer?: (name) => string }
      type: Object,
      default: () => ({ dendrogram: true, colorer: null }),
    },
    layout: { // { dendrogram: boolean }
      type: String,
      validate: (v) => heatmapLayouts.find((d) => d.value === v),
      default: heatmapLayouts[0].value,
    },
    transposed: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      format: format('.4e'),
      legendGradient: `linear-gradient(to right, ${schemeRdBu[5][4]} 0%, ${schemeRdBu[5][2]} 50%, ${schemeRdBu[5][0]} 100%)`,
      padding: 8,
      width: 0,
      height: 0,
      refsMounted: false,
      column: {
        hovered: new Set(),
        collapsed: new Set(),
        focus: null,
      },
      row: {
        hovered: new Set(),
        collapsed: new Set(),
        focus: null,
      },
      DENDROGRAM_RATIO,
      LABEL_WIDTH,
    };
  },
  computed: {
    padding2() {
      return this.padding * 2;
    },
    reactiveColumnUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateColumn();
      return '';
    },
    reactiveRowUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateRow();
      return '';
    },
    reactiveMatrixUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateMatrix();
      return '';
    },
    reactiveRowLabelUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateRowLabel();
      return '';
    },
    reactiveColumnLabelUpdate() {
      if (!this.refsMounted) {
        return '';
      }
      this.updateColumnLabel();
      return '';
    },

    columnTree() {
      return this.computeTree(this.columnClustering, this.column);
    },

    columnHierarchy() {
      return this.computeHierarchy(this.columnTree, this.matrixWidth, this.height);
    },

    rowTree() {
      return this.computeTree(this.rowClustering, this.row);
    },

    rowHierarchy() {
      const root = this.computeHierarchy(this.rowTree, this.matrixHeight, this.width);
      if (!root) {
        return root;
      }
      root.each((node) => {
        const t = node.x;
        node.x = node.y;
        node.y = t;
      });
      return root;
    },
    valueScale() {
      return scaleSequential((t) => interpolateRdBu(1 - t)).domain(domain(this.values));
    },
    legendDomain() {
      return this.valueScale.domain().map(this.format);
    },

    columnLeaves() {
      return this.columnConfig.dendrogram ? this.columnLeavesSorted : this.columnLeavesOriginal;
    },

    columnLeavesSorted() {
      return this.columnTree ? this.columnTree.leaves() : [];
    },

    columnLeavesOriginal() {
      const {
        columnLeavesSorted,
        original,
        transposed,
      } = this;

      // Make a lookup table of the leaves by leaf name.
      const lookup = new Map();
      columnLeavesSorted.forEach((leaf) => {
        lookup.set(leaf.data.name, leaf);
      });

      // Reorder the leaves by the order given in the clustering prop.
      const source = transposed ? original.rows : original.columns;
      return source.map((name) => lookup.get(name));
    },

    rowLeaves() {
      return this.rowConfig.dendrogram ? this.rowLeavesSorted : this.rowLeavesOriginal;
    },

    rowLeavesSorted() {
      return this.rowTree ? this.rowTree.leaves() : [];
    },

    rowLeavesOriginal() {
      const {
        rowLeavesSorted,
        original,
        transposed,
      } = this;

      // Make a lookup table of the leaves by leaf name.
      const lookup = new Map();
      rowLeavesSorted.forEach((leaf) => {
        lookup.set(leaf.data.name, leaf);
      });

      // Reorder the leaves by the order given in the clustering prop.
      const source = transposed ? original.columns : original.rows;
      return source.map((name) => lookup.get(name));
    },

    columnDendrogramHeight() {
      return this.columnConfig.dendrogram ? this.height * DENDROGRAM_RATIO : 0;
    },
    rowDendrogramWidth() {
      return this.rowConfig.dendrogram ? this.width * DENDROGRAM_RATIO : 0;
    },
    matrixDimensions() {
      let width = Math.max(this.width - this.rowDendrogramWidth - LABEL_WIDTH, 0);
      let height = Math.max(this.height - this.columnDendrogramHeight - LABEL_WIDTH, 0);
      if (this.layout === 'squareCells') {
        const wx = width / this.columnLeaves.length;
        const hy = height / this.rowLeaves.length;
        const ci = Math.min(wx, hy);
        width = ci * this.columnLeaves.length;
        height = ci * this.rowLeaves.length;
      } else if (this.layout === 'full') {
        width = this.columnLeaves.length * (MAX_FONT_SIZE + 2);
        height = this.rowLeaves.length * (MAX_FONT_SIZE + 2);
      } else if (this.layout === 'squareMatrix') {
        width = Math.min(width, height);
        height = width;
      }
      return { width, height };
    },
    matrixWidth() {
      return this.matrixDimensions.width;
    },
    matrixHeight() {
      return this.matrixDimensions.height;
    },
    fontSize() {
      const wx = this.matrixWidth / this.columnLeaves.length - 2;
      const hy = this.matrixHeight / this.rowLeaves.length - 2;

      return Math.min(wx, hy, MAX_FONT_SIZE);
    },
  },
  mounted() {
    this.onResize();
    this.refsMounted = true;
  },

  methods: {
    computeTree(node, { collapsed, focus }) {
      if (!node) {
        return null;
      }
      const injectIndices = (s) => {
        if (typeof s.index === 'number') {
          s.indices = [s.index];
          s.names = [s.name];
        } else {
          s.indices = [].concat(...s.children.map(injectIndices));
          s.names = [].concat(...s.children.map((c) => c.names));
          s.name = s.names.join(', ');
        }
        return s.indices;
      };

      injectIndices(node);

      let root = hierarchy(node,
        (d) => (collapsed.has(d) ? [] : (d.children || [])))
        .count()
        .sort((a, b) => b.height - a.height || b.data.index - a.data.index);

      if (focus) {
        // find the focus node and it is the new root
        root.each((n) => {
          if (n.data === focus) {
            root = n;
          }
        });
      }
      return root;
    },
    computeHierarchy(root, layoutWidth, layoutHeight) {
      if (!root) {
        return null;
      }
      const l = cluster()
        .size([layoutWidth, layoutHeight * DENDROGRAM_RATIO - this.padding2])
        .separation(() => 1);
      return l(root);
    },
    updateTree(ref, root, wrapper, config, horizontalLayout) {
      if (!ref || !config.dendrogram || !root) {
        return;
      }
      const svg = select(ref);
      const edges = svg.select('g.edges').selectAll('path').data(root.links()).join((enter) => {
        const r = enter.append('path');
        r.on('mouseenter', (d) => {
          changeHovered(wrapper, d.target.data.indices);
        }).on('mouseleave', () => {
          changeHovered(wrapper, null);
        });
        return r;
      });
      const { hovered, collapsed } = wrapper;
      const { padding } = this;

      edges.classed('selected', (d) => d.target.data.indices.some((l) => hovered.has(l)));

      const renderVerticalLinks = (d) => `
        M${d.target.x},${d.target.y + (d.target.children ? 0 : padding)}
        L${d.target.x},${d.source.y}
        L${d.source.x},${d.source.y}
      `;
      const renderHorizontalLinks = (d) => `
        M${d.target.x + (d.target.children ? 0 : padding)},${d.target.y}
        L${d.source.x},${d.target.y}
        L${d.source.x},${d.source.y}
      `;

      edges.attr('d', horizontalLayout ? renderVerticalLinks : renderHorizontalLinks);

      const innerNodes = root.descendants().filter((d) => d.data.indices.length > 1);
      const inner = svg.select('g.nodes').selectAll('g').data(innerNodes).join((enter) => {
        const r = enter.append('g')
          .html(`<circle r="${padding}"></circle><text><text><title></title>`)
          .attr('transform', (d) => `translate(${d.x},${d.y})`);
        r.on('click', (d) => {
          if (wrapper.focus === d.data) {
            wrapper.focus = null;
          } else if (event.ctrlKey || event.shiftKey) {
            wrapper.focus = d.data;
          } else if (wrapper.collapsed.has(d.data)) {
            wrapper.collapsed.delete(d.data);
            wrapper.collapsed = new Set(wrapper.collapsed);
          } else {
            wrapper.collapsed.add(d.data);
            wrapper.collapsed = new Set(wrapper.collapsed);
          }
        }).on('mouseenter', (d) => {
          changeHovered(wrapper, d.data.indices);
        }).on('mouseleave', () => {
          changeHovered(wrapper, null);
        });
        return r;
      });

      inner.select('text').text((d) => {
        if (wrapper.focus === d.data) {
          return MDI_STAR_CIRCLE;
        }
        return collapsed.has(d.data) ? MDI_PLUS_CIRCLE : MDI_MINUS_CIRCLE;
      });
      inner.select('title').text((d) => d.data.name);
      inner.classed('collapsed', (d) => collapsed.has(d.data));
      inner.classed('focused', (d) => wrapper.focus === d.data);

      inner.attr('transform', (d) => `translate(${d.x},${d.y})`);
    },
    updateColumn() {
      if (this.columnDendrogramHeight === 0) {
        return;
      }
      this.updateTree(this.$refs.column, this.columnHierarchy, this.column,
        this.columnConfig, true);
    },
    updateRow() {
      if (this.rowDendrogramWidth === 0) {
        return;
      }
      this.updateTree(this.$refs.row, this.rowHierarchy, this.row, this.rowConfig, false);
    },

    combineColor(names, colorer) {
      if (names.length === 1) {
        return colorer(names[0]);
      }
      const frequencies = new Map();
      names.forEach((name) => {
        const color = colorer(name);
        frequencies.set(color, (frequencies.get(color) || 0) + 1);
      });
      // most frequent color
      return Array.from(frequencies.entries()).sort((a, b) => b[1] - a[1])[0][0];
    },
    updateLabel(ref, wrapper, labels, colorer) {
      if (!ref) {
        return;
      }
      const div = select(ref);
      const text = div.selectAll('div').data(labels).join((enter) => {
        const l = enter.append('div');
        l.append('span').classed('color', true);
        l.append('span').classed('label', true);
        return l;
      });
      const { hovered } = wrapper;

      text.classed('selected', (d) => d.data.indices.some((l) => hovered.has(l)));

      text.select('.label').text((d) => d.data.name);
      text.select('.color')
        .classed('hidden', !colorer)
        .style('background', colorer ? ((d) => this.combineColor(d.data.names, colorer)) : null);
    },
    updateColumnLabel() {
      this.updateLabel(this.$refs.collabel, this.column, this.columnLeaves,
        this.columnConfig.colorer, true);
    },
    updateRowLabel() {
      this.updateLabel(this.$refs.rowlabel, this.row, this.rowLeaves,
        this.rowConfig.colorer, false);
    },
    updateMatrix() {
      if (!this.$refs.matrix || !this.values) {
        return;
      }
      const ctx = this.$refs.matrix.getContext('2d');
      ctx.canvas.width = this.matrixWidth;
      ctx.canvas.height = this.matrixHeight;
      ctx.clearRect(0, 0, this.matrixWidth, this.matrixHeight);
      const rows = this.rowLeaves;
      const columns = this.columnLeaves;
      const {
        valueScale,
        values,
        transposed,
      } = this;
      const hoveredRow = this.row.hovered;
      const hoveredColumn = this.column.hovered;

      const w = this.matrixWidth / columns.length;
      const h = this.matrixHeight / rows.length;

      ctx.strokeStyle = 'orange';

      // work on copy for speed
      const data = values.map((r) => r.slice());

      const cnodeIndices = columns.map((n) => n.data.indices);

      rows.forEach((rnode, i) => {
        const rnodeIndices = rnode.data.indices;
        const rowSelected = rnodeIndices.some((s) => hoveredRow.has(s));
        cnodeIndices.forEach((indices, j) => {
          const v = aggregate(data, rnodeIndices, indices, transposed);
          ctx.fillStyle = valueScale(v);
          ctx.fillRect(j * w, i * h, w, h);
        });

        if (rowSelected) {
          ctx.beginPath();
          ctx.moveTo(0, i * h);
          ctx.lineTo(ctx.canvas.width, i * h);
          ctx.moveTo(0, i * h + h);
          ctx.lineTo(ctx.canvas.width, i * h + h);
          ctx.stroke();
        }
      });

      cnodeIndices.forEach((indices, j) => {
        const columnSelected = indices.some((s) => hoveredColumn.has(s));
        if (columnSelected) {
          ctx.beginPath();
          ctx.moveTo(j * w, 0);
          ctx.lineTo(j * w, ctx.canvas.height);
          ctx.moveTo(j * w + w, 0);
          ctx.lineTo(j * w + w, ctx.canvas.height);
          ctx.stroke();
        }
      });
    },
    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width;
      this.height = bb.height;
    },
    canvasMouseMove(evt) {
      const canvas = evt.currentTarget;
      const w = canvas.width / this.columnLeaves.length;
      const h = canvas.height / this.rowLeaves.length;

      const j = Math.floor(Math.max(evt.offsetX, 0) / w);
      const i = Math.floor(Math.max(evt.offsetY, 0) / h);

      const rnode = this.rowLeaves[i].data;
      const cnode = this.columnLeaves[j].data;
      const rowChanged = changeHovered(this.row, rnode.indices);
      const colChanged = changeHovered(this.column, cnode.indices);

      if (rowChanged || colChanged) {
        canvas.title = `${rnode.name} x ${cnode.name} = ${this.format(aggregate(this.values, rnode.indices, cnode.indices, this.transposed))}`;
      }
    },
    canvasMouseLeave() {
      changeHovered(this.row, null);
      changeHovered(this.column, null);
    },

    generateImage() {
      const canvas = document.createElement('canvas');
      const columnDendrogram = this.columnConfig.dendrogram ? this.height * DENDROGRAM_RATIO : 0;
      const rowDendrogram = this.rowConfig.dendrogram ? this.width * DENDROGRAM_RATIO : 0;

      canvas.width = rowDendrogram + this.matrixWidth + LABEL_WIDTH;
      canvas.height = columnDendrogram + this.matrixHeight + LABEL_WIDTH;

      const ctx = canvas.getContext('2d');
      // copy matrix first
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(this.$refs.matrix, rowDendrogram, columnDendrogram);

      const toWait = [];

      if (columnDendrogram > 0) {
        // column dendrogram
        const url = svg2url(this.$refs.column, { font: false, icons: true });
        const img = new Image(this.width * DENDROGRAM_RATIO, this.matrixHeight);
        toWait.push(new Promise((resolve) => {
          img.onload = () => {
            ctx.drawImage(img, rowDendrogram, 0);
            URL.revokeObjectURL(url);
            resolve();
          };
          img.src = url;
        }));
      }
      if (rowDendrogram > 0) {
        // row dendrogram
        const url = svg2url(this.$refs.row, { font: false, icons: true });
        const img = new Image(this.matrixWidth, this.height * DENDROGRAM_RATIO);
        toWait.push(new Promise((resolve) => {
          img.onload = () => {
            ctx.drawImage(img, 0, columnDendrogram);
            URL.revokeObjectURL(url);
            resolve();
          };
          img.src = url;
        }));
      }

      // row labels
      {
        ctx.save();
        ctx.translate(rowDendrogram + this.matrixWidth, columnDendrogram);
        const hi = this.matrixHeight / this.rowLeaves.length;
        const { colorer } = this.rowConfig;
        if (colorer) {
          this.rowLeaves.forEach((d, i) => {
            ctx.fillStyle = this.combineColor(d.data.names, colorer);
            ctx.fillRect(0, hi * i, 5, hi);
          });
        }
        const x = colorer ? 7 : 0;

        ctx.font = window.getComputedStyle(this.$refs.rowlabel).font;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'black';
        this.rowLeaves.forEach((d, i) => {
          ctx.fillText(d.data.name, x, hi * (i + 0.5));
        });
        ctx.restore();
      }
      // column labels
      {
        ctx.save();
        ctx.translate(rowDendrogram, columnDendrogram + this.matrixHeight);
        const wi = this.matrixWidth / this.columnLeaves.length;
        const { colorer } = this.columnConfig;
        if (colorer) {
          this.columnLeaves.forEach((d, i) => {
            ctx.fillStyle = this.combineColor(d.data.names, colorer);
            ctx.fillRect(wi * i, 0, wi, 5);
          });
        }
        const y = colorer ? 7 : 0;
        ctx.font = window.getComputedStyle(this.$refs.collabel).font;
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = 'black';
        this.columnLeaves.forEach((d, i) => {
          ctx.save();
          ctx.translate(wi * (i + 0.5), y);
          ctx.rotate(Math.PI * -0.5);
          ctx.fillText(d.data.name, 0, 0);
          ctx.restore();
        });
        ctx.restore();
      }

      return Promise.all(toWait).then(() => canvas.toDataURL('image/png'));
    },
  },
};
</script>

<template>
  <div
    v-resize:throttle="onResize"
    :class="{
      'grid': true,
      'grid--large': layout === 'full',
    }"
  >
    <svg
      v-show="columnConfig.dendrogram"
      ref="column"
      class="column"
      :width="matrixWidth"
      :height="height * DENDROGRAM_RATIO"
      xmlns="http://www.w3.org/2000/svg"
      :data-update="reactiveColumnUpdate"
    >
      <g
        class="edges"
        :transform="`translate(0,${padding})`"
      />
      <g
        class="nodes"
        :transform="`translate(0,${padding})`"
      />
    </svg>
    <svg
      v-show="rowConfig.dendrogram"
      ref="row"
      class="row"
      :width="width * DENDROGRAM_RATIO"
      :height="matrixHeight"
      xmlns="http://www.w3.org/2000/svg"
      :data-update="reactiveRowUpdate"
    >
      <g
        class="edges"
        :transform="`translate(${padding},0)`"
      />
      <g
        class="nodes"
        :transform="`translate(${padding},0)`"
      />
    </svg>
    <canvas
      ref="matrix"
      class="matrix"
      :data-update="reactiveMatrixUpdate"
      @mousemove="canvasMouseMove($event)"
      @mouseleave="canvasMouseLeave()"
    />
    <div
      ref="collabel"
      class="collabel"
      :style="{fontSize: fontSize+'px', width: matrixWidth+'px', height: LABEL_WIDTH+'px'}"
      :data-update="reactiveColumnLabelUpdate"
    />
    <div
      ref="rowlabel"
      class="rowlabel"
      :style="{fontSize: fontSize+'px', width: LABEL_WIDTH+'px', height: matrixHeight+'px'}"
      :data-update="reactiveRowLabelUpdate"
    />
    <div
      v-show="columnConfig.dendrogram &amp;&amp; rowConfig.dendrogram"
      class="legend-wrapper"
    >
      <div
        class="legend"
        :data-from="legendDomain[0]"
        :data-to="legendDomain[1]"
        :style="{background: legendGradient}"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">

.grid {
  position: absolute;
  top: 4px;
  left: 4px;
  right: 8px;
  bottom: 8px;
  display: grid;
  grid-template-areas: "legend column dl" "row matrix rlabel" "rc clabel ll";
  justify-content: center;
  align-content: center;

  &--large {
    position: relative;
    justify-content: left;
  }
}

.column {
  grid-area: column;
}

.row {
  grid-area: row;
}

.matrix {
  grid-area: matrix;
}

.legend-wrapper {
  grid-area: legend;
  display: flex;
  flex-direction: column;
}

.legend {
  height: 1.5em;
  margin: 2em;
  position: relative;
  &::before {
    content: attr(data-from);
    position: absolute;
    top: 100%;
  }
  &::after {
    content: attr(data-to);
    position: absolute;
    top: 100%;
    right: 0;
  }
}

.collabel {
  grid-area: clabel;
  display: flex;
  justify-content: center;
  overflow: hidden;
  line-height: normal;
  /deep/ div {
    flex-direction: column;
    flex: 1 1 0;
    display: flex;
    align-items: center;
  }
  /deep/ .label {
    text-align: right;
    writing-mode: tb;
    transform: rotate(-180deg);
    flex: 1 1 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  /deep/ .color {
    align-self: stretch;
    height: 5px;
    margin-bottom: 2px;
  }
  /deep/ .selected {
    color: orange;
  }
}

.rowlabel {
  grid-area: rlabel;
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: normal;
  /deep/ .color {
    align-self: stretch;
    width: 5px;
    min-width: 5px;
    margin-right: 2px;
  }
  /deep/ .color.hidden {
    display: none;
  }
  /deep/ div {
    flex: 1 1 0;
    display: flex;
    align-items: center;
  }
  /deep/ .label {
    flex: 1 1 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  /deep/ .selected {
    color: orange;
  }
}

.edges {
  /deep/ path {
    fill: none;
    stroke-width: 1;
    stroke: black;
  }
  /deep/ path.selected {
    stroke: orange;
  }
}

.nodes {
  /deep/ g {
    opacity: 0;
    font: normal normal normal 24px/1 "Material Design Icons";
    fill: black;
    cursor: pointer;
    font-size: 150%;
    user-select: none;
    text-anchor: middle;
    dominant-baseline: central;
    /deep/ circle {
      fill: white;
    }
    &:hover {
      opacity: 1;
      fill: orange;
      /deep/ text {
        fill: orange;
      }
    }
  }
}

</style>
