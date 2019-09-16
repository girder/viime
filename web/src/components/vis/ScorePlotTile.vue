<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  props: {
    width: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    height: {
      required: true,
      type: Number,
      validator: Number.isInteger,
    },
    rawPoints: {
      required: true,
      validator: d => d === null || d instanceof Object,
    },
    pcCoords: {
      required: true,
      type: Array,
    },
    columns: {
      required: true,
      type: Array,
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
  },
};

</script>

<template lang="pug">
vis-tile(title="PCA Score Plot")
  score-plot(
      :width="width",
      :height="height",
      :raw-points="rawPoints",
      :pc-coords="pcCoords",
      :columns="columns",
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
</template>
