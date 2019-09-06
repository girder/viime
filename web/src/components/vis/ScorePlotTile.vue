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
    dataset: {
      required: true,
      type: Object,
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
    :dataset="dataset",
    :pc-x="pcX",
    :pc-y="pcY",
    :show-ellipses="showEllipses")
  template(v-slot:controls)
    v-card
      v-layout(column wrap)
        v-flex(px-2 pt-3)
          v-text-field(type="number" label="PC (X Axis)" min="1" max="6" outline v-model="pcXval")
        v-flex(px-2)
          v-text-field(type="number" label="PC (Y Axis)" min="1" max="6" outline v-model="pcYval")
        v-flex
          v-switch(v-model="showEllipses", label="Data ellipses")
</template>
