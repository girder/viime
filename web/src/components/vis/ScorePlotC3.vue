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

    group() {
      const { columns } = this;
      const column = columns.find(elem => elem.column_type === 'group');

      return column.column_header;
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

      const xGrouped = this.grouped(xData);
      const yGrouped = this.grouped(yData);

      const groups = Object.keys(xGrouped);
      let columns = []
      let xs = {};
      groups.forEach(g => {
        const xName = `${g}_x`;

        columns.push([xName, ...xGrouped[g]]);
        columns.push([g, ...yGrouped[g]]);

        xs[g] = xName;
      });

      c3.generate({
        bindto: this.$refs.chart,
        size: {
          width: 600,
          height: 600,
        },
        data: {
          xs,
          columns,
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

  methods: {
    grouped(data) {
      const {
        groupLabels,
        group,
      } = this;

      console.log(groupLabels, group);

      let grouped = {};

      data.forEach((d, i) => {
        const g = groupLabels[group][i];

        if (!Object.prototype.hasOwnProperty.call(grouped, g)) {
          grouped[g] = [];
        }

        grouped[g].push(d);
      });

      return grouped;
    },
  },
};
</script>
