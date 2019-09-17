<template lang="pug">
div
  div(ref="chart")
  span(style="display: none") {{ update }}
</template>

<script>
import c3 from 'c3';
import 'c3/c3.css';

export default {
  props: {
    width: {
      type: Number,
      default: 400,
    },
    height: {
      type: Number,
      default: 300,
    },
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
      validator: prop => Object.values(prop).every(labels => labels.every(val => typeof val === 'string')),
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

    update() {
      const {
        pcCoords,
        pcPoints,
        pcX,
        pcY,
      } = this;

      const x = `PC${pcX}`;
      const y = `PC${pcY}`;

      const [xData, yData] = pcPoints;

      c3.generate({
        bindto: this.$refs.chart,
        size: {
          width: 600,
          height: 600,
        },
        data: {
          xs: {
            // [y]: x,
            PC2: 'PC1',
          },
          columns: [
            [x, ...xData],
            [y, ...yData],
          ],
          type: 'scatter',
        },
        axis: {
          x: {
            label: x,
            tick: {
              fit: false,
            },
          },
          y: {
            label: y,
          },
        },
      });

      return String(Math.random());
    },
  },
};
</script>
