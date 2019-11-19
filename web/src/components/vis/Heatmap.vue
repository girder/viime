<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import resize from 'vue-resize-directive';
import { format } from 'd3-format';
import { hierarchy, cluster, HierarchyNode } from 'd3-hierarchy';
import { scaleSequential } from 'd3-scale';
import { interpolateRdBu, schemeRdBu } from 'd3-scale-chromatic';
import { select, event } from 'd3-selection';
import { svg2url } from '../../utils/exporter';

function domain(arr: number[][]): [number, number] {
  // let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  arr.forEach(row => row.forEach((v) => {
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

function aggregate(
  arr: number[][],
  rs: number[],
  cs: number[],
  transposed: boolean,
) {
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
  const sum = is.reduce(
    (acc, i) => acc + js.reduce((acc2, j) => acc2 + arr[i][j], 0),
    0,
  );
  return sum / l;
}

const DENDOGRAM_RATIO = 0.2;
const LABEL_WIDTH = 150;

const MDI_PLUS_CIRCLE = '\uF417;';
const MDI_MINUS_CIRCLE = '\uF376;';
const MDI_STAR_CIRCLE = '\uF4CF;';

export const heatmapLayouts = [
  { label: 'Auto', value: 'auto' },
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
function changeHovered<T>(wrapper: { hovered: Set<T> }, arr: T[] | null) {
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
  if (
    old.size === 0
    || ((arr.length === 1 && old.has(arr[0])) || arr.every(d => old.has(d)))
  ) {
    return false;
  }

  wrapper.hovered = new Set(arr);
  return true;
}

interface ITreeNode {
  name: string;
  index?: number;
  children?: ITreeNode[];
}

interface IExtendedTreeNode extends ITreeNode {
  names: string[];
  indices: number[];
  children?: IExtendedTreeNode[];
}

declare type IHierarchyNode = HierarchyNode<IExtendedTreeNode> & {
  x?: number;
  y?: number;
};

declare type IHierarchyLink = {
  source: IHierarchyNode;
  target: IHierarchyNode;
}

interface ITreeConfig {
  dendogram: boolean;
  colorer?(name: string): string;
}

interface ITreeState {
  hovered: Set<number>;
  collapsed: Set<ITreeNode>;
  focus: ITreeNode | null;
}

@Component({
  directives: {
    resize,
  },
})
export default class Heatmap extends Vue {
  @Prop({
    default: () => [],
  })
  readonly values!: number[][];

  @Prop({
    default: null,
  })
  readonly columnClustering!: ITreeNode;

  @Prop({
    default: null,
  })
  readonly rowClustering!: ITreeNode;

  @Prop({
    default: () => ({ dendogram: true, colorer: null }),
  })
  readonly rowConfig!: { dendogram: boolean; colorer?(name: string): string };

  @Prop({
    default: () => ({ dendogram: true, colorer: null }),
  })
  readonly columnConfig!: ITreeConfig;

  @Prop({
    default: heatmapLayouts[0].value,
  })
  readonly layout!: string;

  @Prop({
    default: false,
  })
  readonly transposed!: boolean;

  private readonly format = format('.4e');

  readonly legendGradient = `linear-gradient(to right, ${schemeRdBu[5][4]} 0%, ${schemeRdBu[5][2]} 50%, ${schemeRdBu[5][0]} 100%)`;

  readonly padding = 8;

  private width = 0;

  private height = 0;

  private refsMounted = false;

  private column: ITreeState = {
    hovered: new Set(),
    collapsed: new Set(),
    focus: null,
  };

  private row: ITreeState = {
    hovered: new Set(),
    collapsed: new Set(),
    focus: null,
  };

  readonly DENDOGRAM_RATIO = DENDOGRAM_RATIO;

  readonly LABEL_WIDTH = LABEL_WIDTH;

  $refs!: {
    matrix: HTMLCanvasElement;
    collabel: HTMLElement;
    rowlabel: HTMLElement;
    column: SVGSVGElement;
    row: SVGSVGElement;
  };

  get padding2() {
    return this.padding * 2;
  }

  get reactiveColumnUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateColumn();
    return '';
  }

  get reactiveRowUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateRow();
    return '';
  }

  get reactiveMatrixUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateMatrix();
    return '';
  }

  get reactiveRowLabelUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateRowLabel();
    return '';
  }

  get reactiveColumnLabelUpdate() {
    if (!this.refsMounted) {
      return '';
    }
    this.updateColumnLabel();
    return '';
  }

  get columnTree() {
    return Heatmap.computeTree(this.columnClustering, this.column);
  }

  get columnHierarchy() {
    return this.computeHierarchy(
      this.columnTree,
      this.matrixWidth,
      this.height,
    );
  }

  get rowTree() {
    return Heatmap.computeTree(this.rowClustering, this.row);
  }

  get rowHierarchy() {
    const root = this.computeHierarchy(
      this.rowTree,
      this.matrixHeight,
      this.width,
    );
    if (!root) {
      return root;
    }
    root.each((node) => {
      const t = node.x;
      node.x = node.y;
      node.y = t;
    });
    return root;
  }

  get valueScale() {
    return scaleSequential<string>(t => interpolateRdBu(1 - t)).domain(
      domain(this.values),
    );
  }

  get legendDomain() {
    return this.valueScale.domain().map(this.format);
  }

  get columnLeaves() {
    return this.columnTree ? this.columnTree.leaves() : [];
  }

  get rowLeaves() {
    return this.rowTree ? this.rowTree.leaves() : [];
  }

  get columnDendogramHeight() {
    return this.columnConfig.dendogram ? this.height * DENDOGRAM_RATIO : 0;
  }

  get rowDendogramWidth() {
    return this.rowConfig.dendogram ? this.width * DENDOGRAM_RATIO : 0;
  }

  get matrixDimensions() {
    let width = this.width - this.rowDendogramWidth - LABEL_WIDTH;
    let height = this.height - this.columnDendogramHeight - LABEL_WIDTH;
    if (this.layout === 'squareCells') {
      const wx = width / this.columnLeaves.length;
      const hy = height / this.rowLeaves.length;
      const ci = Math.min(wx, hy);
      width = ci * this.columnLeaves.length;
      height = ci * this.rowLeaves.length;
    } else if (this.layout === 'squareMatrix') {
      width = Math.min(width, height);
      height = width;
    }
    return { width, height };
  }

  get matrixWidth() {
    return this.matrixDimensions.width;
  }

  get matrixHeight() {
    return this.matrixDimensions.height;
  }

  get fontSize() {
    const wx = this.matrixWidth / this.columnLeaves.length - 2;
    const hy = this.matrixHeight / this.rowLeaves.length - 2;

    return Math.min(wx, hy, 12);
  }

  mounted() {
    this.onResize();
    this.refsMounted = true;
  }

  static computeTree(
    node: ITreeNode,
    { collapsed, focus }: ITreeState,
  ): IHierarchyNode | null {
    if (!node) {
      return null;
    }
    const injectIndices = (s: IExtendedTreeNode): number[] => {
      if (typeof s.index === 'number') {
        s.indices = [s.index];
        s.names = [s.name];
      } else {
        s.indices = ([] as number[]).concat(...s.children!.map(injectIndices));
        s.names = ([] as string[]).concat(...s.children!.map(c => c.names));
        s.name = s.names.join(', ');
      }
      return s.indices;
    };

    injectIndices(node as IExtendedTreeNode);

    let root = hierarchy(node as IExtendedTreeNode, d => (collapsed.has(d) ? [] : d.children || []))
      .count()
      .sort((a, b) => b.height - a.height || b.data.index! - a.data.index!);

    if (focus) {
      // find the focus node and it is the new root
      root.each((n) => {
        if (n.data === focus) {
          root = n;
        }
      });
    }
    return root;
  }

  computeHierarchy(
    root: IHierarchyNode | null,
    layoutWidth: number,
    layoutHeight: number,
  ): IHierarchyNode | null {
    if (!root) {
      return null;
    }
    const l = cluster<IExtendedTreeNode>()
      .size([layoutWidth, layoutHeight * DENDOGRAM_RATIO - this.padding2])
      .separation(() => 1);
    return l(root);
  }

  updateTree(
    ref: SVGSVGElement,
    root: IHierarchyNode | null,
    wrapper: ITreeState,
    config: ITreeConfig,
    horizontalLayout: boolean,
  ) {
    if (!ref || !config.dendogram || !root) {
      return;
    }
    const svg = select(ref);
    const edges = svg
      .select('g.edges')
      .selectAll<SVGPathElement, unknown>('path')
      .data(root.links())
      .join((enter) => {
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

    edges.classed('selected', d => d.target.data.indices.some(l => hovered.has(l)));

    const renderVerticalLinks = (d: IHierarchyLink) => `
      M${d.target.x},${d.target.y! + (d.target.children ? 0 : padding)}
      L${d.target.x},${d.source.y}
      L${d.source.x},${d.source.y}
    `;
    const renderHorizontalLinks = (d: IHierarchyLink) => `
      M${d.target.x! + (d.target.children ? 0 : padding)},${d.target.y}
      L${d.source.x},${d.target.y}
      L${d.source.x},${d.source.y}
    `;

    edges.attr(
      'd',
      horizontalLayout ? renderVerticalLinks : renderHorizontalLinks,
    );

    const innerNodes = root
      .descendants()
      .filter(d => d.data.indices.length > 1);
    const inner = svg
      .select('g.nodes')
      .selectAll('g')
      .data(innerNodes)
      .join((enter) => {
        const r = enter
          .append('g')
          .html(`<circle r="${padding}"></circle><text><text><title></title>`)
          .attr('transform', d => `translate(${d.x},${d.y})`);
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
        })
          .on('mouseenter', (d) => {
            changeHovered(wrapper, d.data.indices);
          })
          .on('mouseleave', () => {
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
    inner.select('title').text(d => d.data.name);
    inner.classed('collapsed', d => collapsed.has(d.data));
    inner.classed('focused', d => wrapper.focus === d.data);

    inner.attr('transform', d => `translate(${d.x},${d.y})`);
  }

  updateColumn() {
    if (this.columnDendogramHeight === 0) {
      return;
    }
    this.updateTree(
      this.$refs.column,
      this.columnHierarchy,
      this.column,
      this.columnConfig,
      true,
    );
  }

  updateRow() {
    if (this.rowDendogramWidth === 0) {
      return;
    }
    this.updateTree(
      this.$refs.row,
      this.rowHierarchy,
      this.row,
      this.rowConfig,
      false,
    );
  }

  static combineColor(names: string[], colorer: (val: string) => string) {
    if (names.length === 1) {
      return colorer(names[0]);
    }
    const frequencies = new Map<string, number>();
    names.forEach((name) => {
      const color = colorer(name);
      frequencies.set(color, (frequencies.get(color) || 0) + 1);
    });
    // most frequent color
    return Array.from(frequencies.entries()).sort((a, b) => b[1] - a[1])[0][0];
  }

  static updateLabel(
    ref: HTMLElement,
    wrapper: ITreeState,
    labels: IHierarchyNode[],
    colorer?: (val: string) => string,
  ) {
    if (!ref) {
      return;
    }
    const div = select(ref);
    const text = div
      .selectAll('div')
      .data(labels)
      .join((enter) => {
        const l = enter.append('div');
        l.append('span').classed('color', true);
        l.append('span').classed('label', true);
        return l;
      });
    const { hovered } = wrapper;

    text.classed('selected', d => d.data.indices.some(l => hovered.has(l)));

    text.select('.label').text(d => d.data.name);
    const color = text
      .select('.color')
      .classed('hidden', !colorer);
    if (colorer) {
      color.style('background', d => Heatmap.combineColor(d.data.names, colorer));
    }
  }

  updateColumnLabel() {
    Heatmap.updateLabel(
      this.$refs.collabel,
      this.column,
      this.columnLeaves,
      this.columnConfig.colorer,
    );
  }

  updateRowLabel() {
    Heatmap.updateLabel(
      this.$refs.rowlabel,
      this.row,
      this.rowLeaves,
      this.rowConfig.colorer,
    );
  }

  updateMatrix() {
    if (!this.$refs.matrix || !this.values) {
      return;
    }
    const ctx = this.$refs.matrix.getContext('2d')!;
    ctx.canvas.width = this.matrixWidth;
    ctx.canvas.height = this.matrixHeight;
    ctx.clearRect(0, 0, this.matrixWidth, this.matrixHeight);
    const rows = this.rowLeaves;
    const columns = this.columnLeaves;
    const { valueScale, values, transposed } = this;
    const hoveredRow = this.row.hovered;
    const hoveredColumn = this.column.hovered;

    const w = this.matrixWidth / columns.length;
    const h = this.matrixHeight / rows.length;

    ctx.strokeStyle = 'orange';

    // work on copy for speed
    const data = values.map(r => r.slice());

    const cnodeIndices = columns.map(n => n.data.indices);

    rows.forEach((rnode, i) => {
      const rnodeIndices = rnode.data.indices;
      const rowSelected = rnodeIndices.some(s => hoveredRow.has(s));
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
      const columnSelected = indices.some(s => hoveredColumn.has(s));
      if (columnSelected) {
        ctx.beginPath();
        ctx.moveTo(j * w, 0);
        ctx.lineTo(j * w, ctx.canvas.height);
        ctx.moveTo(j * w + w, 0);
        ctx.lineTo(j * w + w, ctx.canvas.height);
        ctx.stroke();
      }
    });
  }

  onResize() {
    const bb = this.$el.getBoundingClientRect();
    this.width = bb.width;
    this.height = bb.height;
  }

  canvasMouseMove(evt: MouseEvent) {
    const canvas = evt.currentTarget as HTMLCanvasElement;
    const w = canvas.width / this.columnLeaves.length;
    const h = canvas.height / this.rowLeaves.length;

    const j = Math.floor(evt.offsetX / w);
    const i = Math.floor(evt.offsetY / h);
    const rnode = this.rowLeaves[i].data;
    const cnode = this.columnLeaves[j].data;
    const rowChanged = changeHovered(this.row, rnode.indices);
    const colChanged = changeHovered(this.column, cnode.indices);

    if (rowChanged || colChanged) {
      canvas.title = `${rnode.name} x ${cnode.name} = ${this.format(
        aggregate(this.values, rnode.indices, cnode.indices, this.transposed),
      )}`;
    }
  }

  canvasMouseLeave() {
    changeHovered(this.row, null);
    changeHovered(this.column, null);
  }

  generateImage() {
    const canvas = document.createElement('canvas');
    const columnDendogram = this.columnConfig.dendogram
      ? this.height * DENDOGRAM_RATIO
      : 0;
    const rowDendogram = this.rowConfig.dendogram
      ? this.width * DENDOGRAM_RATIO
      : 0;

    canvas.width = rowDendogram + this.matrixWidth + LABEL_WIDTH;
    canvas.height = columnDendogram + this.matrixHeight + LABEL_WIDTH;

    const ctx = canvas.getContext('2d')!;
    // copy matrix first
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(this.$refs.matrix, rowDendogram, columnDendogram);

    const toWait = [];

    if (columnDendogram > 0) {
      // column dendogram
      const url = svg2url(this.$refs.column, { font: false, icons: true });
      const img = new Image(this.width * DENDOGRAM_RATIO, this.matrixHeight);
      toWait.push(
        new Promise((resolve) => {
          img.onload = () => {
            ctx.drawImage(img, rowDendogram, 0);
            URL.revokeObjectURL(url);
            resolve();
          };
          img.src = url;
        }),
      );
    }
    if (rowDendogram > 0) {
      // row dendogram
      const url = svg2url(this.$refs.row, { font: false, icons: true });
      const img = new Image(this.matrixWidth, this.height * DENDOGRAM_RATIO);
      toWait.push(
        new Promise((resolve) => {
          img.onload = () => {
            ctx.drawImage(img, 0, columnDendogram);
            URL.revokeObjectURL(url);
            resolve();
          };
          img.src = url;
        }),
      );
    }

    // row labels
    {
      ctx.save();
      ctx.translate(rowDendogram + this.matrixWidth, columnDendogram);
      const hi = this.matrixHeight / this.rowLeaves.length;
      const { colorer } = this.rowConfig;
      if (colorer) {
        this.rowLeaves.forEach((d, i) => {
          ctx.fillStyle = Heatmap.combineColor(d.data.names, colorer);
          ctx.fillRect(0, hi * i, 5, hi);
        });
      }
      const x = colorer ? 7 : 0;

      ctx.font = window.getComputedStyle(this.$refs.rowlabel).font!;
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
      ctx.translate(rowDendogram, columnDendogram + this.matrixHeight);
      const wi = this.matrixWidth / this.columnLeaves.length;
      const { colorer } = this.columnConfig;
      if (colorer) {
        this.columnLeaves.forEach((d, i) => {
          ctx.fillStyle = Heatmap.combineColor(d.data.names, colorer);
          ctx.fillRect(wi * i, 0, wi, 5);
        });
      }
      const y = colorer ? 7 : 0;
      ctx.font = window.getComputedStyle(this.$refs.collabel).font!;
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
  }
}
</script>

<template lang="pug">
.grid(v-resize:throttle="onResize")
  svg.column(ref="column", v-show="columnConfig.dendogram",
      :width="matrixWidth",
      :height="height * DENDOGRAM_RATIO", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveColumnUpdate")
    g.edges(:transform="`translate(0,${padding})`")
    g.nodes(:transform="`translate(0,${padding})`")
  svg.row(ref="row", v-show="rowConfig.dendogram",
      :width="width * DENDOGRAM_RATIO",
      :height="matrixHeight", xmlns="http://www.w3.org/2000/svg",
      :data-update="reactiveRowUpdate")
    g.edges(:transform="`translate(${padding},0)`")
    g.nodes(:transform="`translate(${padding},0)`")
  canvas.matrix(ref="matrix", :data-update="reactiveMatrixUpdate",
      @mousemove="canvasMouseMove($event)", @mouseleave="canvasMouseLeave()")
  .collabel(ref="collabel",
      :style="{fontSize: fontSize+'px', width: this.matrixWidth+'px', height: LABEL_WIDTH+'px'}",
      :data-update="reactiveColumnLabelUpdate")
  .rowlabel(ref="rowlabel",
      :style="{fontSize: fontSize+'px', width: LABEL_WIDTH+'px', height: this.matrixHeight+'px'}",
      :data-update="reactiveRowLabelUpdate")
  .legend-wrapper(v-show="columnConfig.dendogram && rowConfig.dendogram")
    .legend(:data-from="legendDomain[0]", :data-to="legendDomain[1]",
        :style="{background: legendGradient}")
</template>

<style scoped>
.grid {
  position: absolute;
  top: 4px;
  left: 4px;
  right: 8px;
  bottom: 8px;
  display: grid;
  grid-template-areas:
    "legend column dl"
    "row matrix rlabel"
    "rc clabel ll";
  justify-content: center;
  align-content: center;
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
}

.legend::before {
  content: attr(data-from);
  position: absolute;
  top: 100%;
}

.legend::after {
  content: attr(data-to);
  position: absolute;
  top: 100%;
  right: 0;
}

.collabel {
  grid-area: clabel;
  display: flex;
  justify-content: center;
  overflow: hidden;
  line-height: normal;
}

.collabel >>> div {
  flex-direction: column;
}

.collabel >>> .label {
  text-align: right;
  writing-mode: tb;
  transform: rotate(-180deg);
}

.collabel >>> .color {
  align-self: stretch;
  height: 5px;
  margin-bottom: 2px;
}

.rowlabel {
  grid-area: rlabel;
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: normal;
}

.rowlabel >>> .color {
  align-self: stretch;
  width: 5px;
  min-width: 5px;
  margin-right: 2px;
}

.rowlabel >>> .color.hidden {
  display: none;
}

.collabel >>> div,
.rowlabel >>> div {
  flex: 1 1 0;
  display: flex;
  align-items: center;
}

.collabel >>> .label,
.rowlabel >>> .label {
  flex: 1 1 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rowlabel >>> .selected,
.collabel >>> .selected {
  color: orange;
}

.edges >>> path {
  fill: none;
  stroke-width: 1;
  stroke: black;
}

.edges >>> path.selected {
  stroke: orange;
}

.nodes >>> g {
  opacity: 0;
  font: normal normal normal 24px/1 "Material Design Icons";
  fill: black;
  cursor: pointer;
  font-size: 150%;
  user-select: none;
  text-anchor: middle;
  dominant-baseline: central;
}

.nodes >>> g > circle {
  fill: white;
}

.nodes >>> g:hover {
  opacity: 1;
  fill: orange;
}

.nodes >>> g:hover > text {
  fill: orange;
}

.nodes >>> .collapsed,
.nodes >>> .focused {
  opacity: 1;
}
</style>
