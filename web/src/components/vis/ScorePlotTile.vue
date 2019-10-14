<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from './mixins/plotData';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  mixins: [plotData('pca')],

  props: {
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      pcXval: '1',
      pcYval: '2',
      showEllipses: true,
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval, 10);
    },

    pcY() {
      return Number.parseInt(this.pcYval, 10);
    },

    pcCoords() {
      return this.getPlotDataProperty('x', []);
    },

    rowLabels() {
      return this.getPlotDataProperty('rows', []);
    },

    groups() {
      const base = this.getPlotDataProperty('labels', {});
      const groups = Object.keys(base);
      if (groups.length === 0) {
        return [];
      }
      if (groups.length === 1) {
        return base[groups[0]];
      }
      // find the right one, since it is a mix of group and column
      const group = this.dataset.validatedGroups
        ? this.dataset.validatedGroups.columnNames[0] : groups[0];
      return base[group] || [];
    },

    groupToColor() {
      const levels = this.dataset.groupLevels;
      const lookup = new Map(levels.map(({ name, color }) => [name, color]));
      return group => lookup.get(group) || null;
    },

    eigenvalues() {
      return this.getPlotDataProperty('sdev', []);
    },
  },
};

</script>

<template lang="pug">
vis-tile(v-if="plot", title="PCA Score Plot", :loading="plot.loading", svg-download)
  score-plot(
      v-if="plot && dataset.ready",
      :pc-coords="pcCoords",
      :row-labels="rowLabels",
      :groups="groups",
      :group-to-color="groupToColor",
      :eigenvalues="eigenvalues",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-ellipses="showEllipses")
  template(v-slot:controls)
    v-menu(bottom, offset-y, left, :min-width="150", :close-on-content-click="false")
      template(v-slot:activator="{ on }")
        v-btn(v-on="on", icon)
          v-icon.mdi.mdi-dots-vertical

      v-card.pa-1(flat)
        v-layout.px-2(column)
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (X Axis)",
              min="1",
              outline,
              v-model="pcXval")
          v-text-field.py-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              outline,
              v-model="pcYval")
          v-switch.py-2(v-model="showEllipses", label="Data ellipses", hide-details)
  template(v-slot:help)
    p.
      This chart shows Principal Component Analysis (PCA) scores as a
      scatter plot. When the chart first appears, it displays the first two
      principal components on the x and y axes.

    p.
      The dataset's group column is used to partition the observations into
      groups by color; each group's data points are plotted along with a
      confidence ellipse illustrating one standard deviation in the group's
      primary and secondary directions.

    p.
      The control panel contains a few settings you can use to change how the
      PCA score data is displayed: the number fields allow you to choose which
      two PCs are plotted, while the toggle switch enables turning the
      confidence ellipses on and off. As the PCs are changed, note that the
      percent of total variance accounted for by each component is displayed
      within the axis label.

</template>
