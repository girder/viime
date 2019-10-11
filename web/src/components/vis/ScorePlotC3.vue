<template lang="pug">
div(v-resize:throttle="onResize")
  div(ref="chart")
  span(style="display: none") {{ update }}
</template>

<style>
.c3 text {
  font-family: Barlow Condensed;
}
</style>

<script>
import c3 from 'c3';
import { select } from 'd3-selection';
import { deviation, mean } from 'd3-array';
import { format } from 'd3-format';
import resize from 'vue-resize-directive';

import 'c3/c3.css';

function covar(xs, ys) {
  const e_xy = mean(xs.map((x, i) => x * ys[i]));
  const e_xx = mean(xs);
  const e_yy = mean(ys);

  return e_xy - e_xx * e_yy;
}

// Create a plot of the covariance confidence ellipse of `x` and `y`.
// x, y : array_like, shape (n, )
//     Input data.
// std : float
//     The number of standard deviations to determine the ellipse's radiuses.
//
// Port of Python function from:
//      https://matplotlib.org/gallery/statistics/confidence_ellipse.html
function confidenceEllipse(x, y, std) {
  // cov = np.cov(x, y)
  const xdev = deviation(x);
  const ydev = deviation(y);
  const xcov = xdev * xdev;
  const ycov = ydev * ydev;
  const xycov = covar(x, y);

  // pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
  const pearson = xycov / Math.sqrt(xcov * ycov);

  // # Using a special case to obtain the eigenvalues of this
  // # two-dimensionl dataset.
  // ell_radius_x = np.sqrt(1 + pearson)
  // ell_radius_y = np.sqrt(1 - pearson)
  const ell_radius_x = Math.sqrt(1 + pearson);
  const ell_radius_y = Math.sqrt(1 - pearson);

  // # Calculating the stdandard deviation of x from
  // # the squareroot of the variance and multiplying
  // # with the given number of standard deviations.
  // scale_x = np.sqrt(cov[0, 0]) * n_std
  // mean_x = np.mean(x)
  const scale_x = Math.sqrt(xcov) * std;
  const mean_x = mean(x);

  // # calculating the stdandard deviation of y ...
  // scale_y = np.sqrt(cov[1, 1]) * n_std
  // mean_y = np.mean(y)
  const scale_y = Math.sqrt(ycov) * std;
  const mean_y = mean(y);

  // transf = transforms.Affine2D() \
  //     .rotate_deg(45) \
  //     .scale(scale_x, scale_y) \
  //     .translate(mean_x, mean_y)
  const transform = `translate(${mean_x} ${mean_y}) scale(${scale_x} ${scale_y}) rotate(45)`;

  return { rx: ell_radius_x, ry: ell_radius_y, transform };
}

export default {
  directives: {
    resize,
  },
  props: {
    pcX: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    pcY: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    showEllipses: {
      type: Boolean,
      default: true,
    },
    pcCoords: {
      required: true,
      type: Array,
      validator: prop => prop.every(coord => coord.every(Number.isFinite)),
    },
    rowLabels: {
      required: true,
      type: Array,
      validator: prop => prop.every(val => typeof val === 'string'),
    },
    groupLabels: {
      required: true,
      type: Object,
    },
    eigenvalues: {
      required: true,
      type: Array,
      validator: prop => prop.every(Number.isFinite),
    },
    columns: {
      required: true,
      type: Array,
      validator: prop => prop.every(column => ['column_header', 'column_type'].every(key => Object.prototype.hasOwnProperty.call(column, key))),
    },
  },

  data() {
    return {
      chart: null,
      ellipseVisible: {},
      duration: 500,
      width: 100,
      height: 100,
    };
  },

  computed: {
    pcPoints() {
      const {
        pcCoords,
        pcX,
        pcY,
      } = this;

      const x = pcCoords.map(p => p[pcX - 1]);
      const y = pcCoords.map(p => p[pcY - 1]);

      return [x, y];
    },

    totalVariance() {
      const {
        eigenvalues,
      } = this;

      return eigenvalues.reduce((acc, x) => acc + x, 0);
    },

    pcVariances() {
      const {
        pcX,
        pcY,
        eigenvalues,
        totalVariance,
      } = this;

      return [
        eigenvalues[pcX - 1] / totalVariance,
        eigenvalues[pcY - 1] / totalVariance,
      ];
    },

    group() {
      const { columns } = this;
      const column = columns.find(elem => elem.column_type === 'group');

      return column.column_header;
    },

    valid() {
      const {
        pcCoords,
        rowLabels,
        groupLabels,
        eigenvalues,
      } = this;

      return this.$refs.chart
        && pcCoords.length > 0
        && rowLabels.length > 0
        && Object.keys(groupLabels).length > 0
        && eigenvalues.length > 0;
    },

    update() {
      const {
        pcCoords,
        pcPoints,
        pcX,
        pcY,
        showEllipses,
        ellipseVisible,
        duration,
        pcVariances,
        valid,
        width,
        height,
      } = this;

      if (!valid) {
        return '';
      }

      const fmt = format('.2%');
      const x = `PC${pcX} (${fmt(pcVariances[0])})`;
      const y = `PC${pcY} (${fmt(pcVariances[1])})`;

      this.chart.axis.labels({
        x,
        y,
      });

      this.chart.resize({
        width,
        height,
      });

      const [xData, yData] = pcPoints;

      const xGrouped = this.grouped(xData);
      const yGrouped = this.grouped(yData);

      const groups = Object.keys(xGrouped);
      const columns = [];
      const xs = {};
      groups.forEach((g) => {
        const xName = `${g}_x`;

        columns.push([xName, ...xGrouped[g]]);
        columns.push([g, ...yGrouped[g]]);

        xs[g] = xName;
      });

      // Draw the C3 chart.
      this.chart.load({
        columns,
        xs,
      });

      // Draw the data ellipses.
      const scaleX = this.chart.internal.x;
      const scaleY = this.chart.internal.y;
      const cmap = this.chart.internal.color;

      const confidenceEllipses = Object.keys(xGrouped).map(group => ({
        ...confidenceEllipse(xGrouped[group], yGrouped[group], 1),
        category: group,
      }));
      confidenceEllipses.forEach(ell => {
        if (ellipseVisible[ell.category] === undefined) {
          ellipseVisible[ell.category] = true;
        }
      });

      const xFactor = (scaleX(1e10) - scaleX(0)) / 1e10;
      const yFactor = (scaleY(1e10) - scaleY(0)) / 1e10;
      const plotTransform = `translate(${scaleX(0)} ${scaleY(0)}) scale(${xFactor} ${yFactor})`;
      select(this.$refs.chart)
        .select('.c3-custom-ellipses')
        .selectAll('ellipse')
        .data(confidenceEllipses)
        .join(
          enter => enter
            .append('ellipse')
            .attr('class', d => `ellipse-${d.category}`)
            .classed('ellipse', true)
            .style('fill', 'none')
            .style('stroke', d => cmap(d.category))
            .style('stroke-width', 1)
            .attr('vector-effect', 'non-scaling-stroke')
            .attr('rx', d => d.rx)
            .attr('ry', d => d.ry)
            .attr('transform', d => `${plotTransform} ${d.transform}`)
            .style('opacity', 1),
          update => update
            .attr('rx', d => d.rx)
            .attr('ry', d => d.ry)
            .attr('transform', d => `${plotTransform} ${d.transform}`)
            .style('display', (d) =>
              showEllipses && ellipseVisible[d.category] ? null : 'none'),
          exit => exit.transition('exit')
            .duration(duration)
            .style('opacity', 0)
            .remove(),
        );

      return String(Math.random());
    },
  },

  mounted() {
    this.chart = c3.generate({
      bindto: this.$refs.chart,
      data: {
        columns: [],
        type: 'scatter',
      },
      axis: {
        x: {
          label: {
            text: 'x',
            position: 'outer-center',
          },
          tick: {
            fit: false,
          },
        },
        y: {
          label: {
            text: 'y',
            position: 'outer-middle',
          },
        },
      },
      legend: {
        item: {
          onmouseover: (id) => {
            this.chart.focus(id);
            this.focusEllipse(id);
          },

          onmouseout: () => {
            this.chart.focus();
            this.focusEllipse();
          },

          onclick: (id) => {
            this.chart.toggle(id);
            const showing = this.toggleEllipse(id);

            if (!showing) {
              this.chart.focus();
              this.focusEllipse();
            }
          },
        },
      },
    });

    select(this.$refs.chart)
      .select('.c3-chart')
      .append('g')
      .classed('c3-custom-ellipses', true);
  },

  methods: {
    grouped(data) {
      const {
        groupLabels,
        group,
      } = this;

      const grouped = {};

      data.forEach((d, i) => {
        const g = groupLabels[group][i];

        if (!Object.prototype.hasOwnProperty.call(grouped, g)) {
          grouped[g] = [];
        }

        grouped[g].push(d);
      });

      return grouped;
    },

    focusEllipse(which) {
      const selector = which ? `ellipse.ellipse-${which}` : 'ellipse.ellipse';

      this.defocusEllipse();

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 1.0);
    },

    defocusEllipse(which) {
      const selector = which ? `ellipse.ellipse-${which}` : 'ellipse.ellipse';

      select(this.$refs.chart)
        .selectAll(selector)
        .style('opacity', 0.3);
    },

    showEllipse(which) {
      const selector = `ellipse.ellipse-${which}`;

      select(this.$refs.chart)
        .select(selector)
        .style('display', null);
    },

    hideEllipse(which) {
      const selector = `ellipse.ellipse-${which}`;

      select(this.$refs.chart)
        .select(selector)
        .style('display', 'none');
    },

    toggleEllipse2(which) {
      const selector = `ellipse.ellipse-${which}`;

      const showing = this.ellipseShowing(which);

      (showing ? this.hideEllipse : this.showEllipse)(which);
    },

    toggleEllipse(which) {
      this.ellipseVisible[which] = !this.ellipseVisible[which];
      return this.ellipseVisible[which];
    },

    ellipseShowing(which) {
      const selector = `ellipse.ellipse-${which}`;

      const showing = select(this.$refs.chart)
        .select(selector)
        .style('display') !== 'none';

      return showing;
    },

    setEllipseVisibility(on) {
      const visible =
        select(this.$refs.chart).select('.ellipse').style('display') !== 'none';

      if (on === visible) {
        return;
      }

      const opacity = on ? 1.0 : 0.0;

      const sel = select(this.$refs.chart)
        .selectAll('.ellipse');

      if (on) {
        sel.style('opacity', 0.0)
          .style('display', null);
      }

      const t = sel.transition()
        .duration(this.duration)
        .style('opacity', opacity);

      t.on('end', () => {
        if (!on) {
          sel.style('display', 'none')
            .style('opacity', 1.0);
        }
      });
    },

    onResize() {
      const bb = this.$el.getBoundingClientRect();
      this.width = bb.width - 20;
      this.height = bb.height;
    },
  },
};
</script>
