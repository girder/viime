<script>
import ScorePlot from '@/components/vis/ScorePlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    ScorePlot,
    VisTile,
  },

  props: {
    id: {
      type: String,
      required: true,
    },

    pcX: {
      type: Number,
      validator: (prop) => Number.isInteger(prop),
      required: true,
    },

    pcY: {
      type: Number,
      validator: (prop) => Number.isInteger(prop),
      required: true,
    },

    showEllipses: {
      type: Boolean,
      required: true,
    },

    pcCoords: {
      type: Array,
      required: true,
    },

    rowLabels: {
      type: Array,
      required: true,
    },

    groupLabels: {
      type: Object,
      required: true,
    },

    groupLevels: {
      type: Array,
      required: true,
    },

    eigenvalues: {
      type: Array,
      required: true,
    },

    columns: {
      type: Array,
      required: true,
    },
  },
  computed: {
    ready() {
      return this.$store.getters.ready(this.id);
    },
  },

  methods: {
    maybeData(key, dflt) {
      const {
        plot,
      } = this;
      return plot?.data ? plot.data[key] : dflt;
    },
  },
};
</script>

<template lang="pug">
vis-tile(title="PLS-DA Score Plot", svg-download)
  score-plot(
      :pc-coords="pcCoords",
      :row-labels="rowLabels",
      :colors="groupLevels",
      :group-labels="groupLabels",
      :eigenvalues="eigenvalues",
      :columns="columns",
      :pc-x="pcX",
      :pc-y="pcY",
      :show-ellipses="showEllipses")
  //- template(v-slot:help)
  //-   include ../help/ScorePlotHelp.pug
</template>
