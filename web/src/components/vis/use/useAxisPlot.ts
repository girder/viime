import {
  reactive, computed, toRefs, Ref,
} from '@vue/composition-api';
import { Selection } from 'd3-selection';

interface PositionFunc {
  (bbox: DOMRect): number;
}

function labelAxis(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  label: any, msg: string, xFunc: PositionFunc, yFunc: PositionFunc, rot: number,
) {
  const text = label.select('text').html(`${msg}`) as Selection<SVGAElement, unknown, HTMLElement, unknown>;
  const textNode = text.node();
  if (textNode === null) {
    throw new Error('Unexpected null textnode');
  }
  const bbox = textNode.getBBox();
  label.attr('transform', `translate(${xFunc(bbox)},${yFunc(bbox)}) rotate(${rot})`)
    .style('opacity', 1.0);
}

interface Margin {
  top: number;
  left: number;
  bottom: number;
  right: number;
}

export default function useAxisPlot(
  {
    margin,
    width,
    height,
    duration = 500,
    topAxis = false,
  }: {
    margin: Margin;
    width: Ref<number>;
    height: Ref<number>;
    duration?: number;
    topAxis?: boolean;
  },
) {
  const data = reactive({
    axisPlotInitialized: false,
  });

  const dwidth = computed(() => width.value - margin.left - margin.right);
  const dheight = computed(() => height.value - margin.top - margin.bottom);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function axisPlot(svg: any, axisX: any, axisY: any) {
    // Set a "master" SVG group.
    const master = svg.select('g.master').attr('transform', `translate(${margin.left},${margin.top})`);
    const axes = master.select('g.axes');

    const xAxisOffset = (topAxis) ? 0 : dheight.value;

    if (axes.select('.x-axis').size() === 0) {
      axes.append('g')
        .classed('x-axis', true)
        .attr('transform', `translate(0,${xAxisOffset})`)
        .call(axisX);
    } else {
      axes.select('.x-axis')
        .transition()
        .attr('transform', `translate(0,${xAxisOffset})`)
        .duration(duration)
        .call(axisX);
    }

    if (axes.select('.y-axis').size() === 0) {
      axes.append('g')
        .classed('y-axis', true)
        .call(axisY);
    } else {
      axes.select('.y-axis')
        .transition()
        .duration(duration)
        .call(axisY);
    }

    // d3-axis wants to helpfully add font-family:sans-serif, here we remove it
    axes.select('.x-axis').attr('font-family', null);
    axes.select('.y-axis').attr('font-family', null);

    // Conclude the initialization process.
    data.axisPlotInitialized = true;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function setXLabel(svg: any, msg: string) {
    if (!svg.node()) {
      return;
    }
    labelAxis(svg.select('.label.x'),
      msg,
      (bbox: DOMRect) => dwidth.value / 2 - bbox.width / 2,
      (bbox: DOMRect) => dheight.value + margin.bottom / 2 + bbox.height / 2,
      0);
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function setYLabel(svg: any, msg: string) {
    if (!svg.node()) {
      return;
    }

    labelAxis(svg.select('.label.y'),
      msg,
      (bbox: DOMRect) => -margin.left / 2 - bbox.height / 2,
      (bbox: DOMRect) => dheight.value / 2 + bbox.width / 2,
      -90);
  }

  return {
    ...toRefs(data),
    dwidth,
    dheight,
    axisPlot,
    setXLabel,
    setYLabel,
  };
}
