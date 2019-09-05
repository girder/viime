<script>
import LoadingsPlot from '@/components/vis/LoadingsPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    LoadingsPlot,
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
    points: {
      required: true,
    },
  },

  data() {
    return {
      pcXval: "1",
      pcYval: "2",
    };
  },
}

</script>

<template lang="pug">
vis-tile(title="PCA Loadings Plot")
  loadings-plot(:width="width", :height="height", :points="points")
  template(v-slot:controls)
    v-card
      v-layout(column wrap)
        v-flex(px-2 pt-3)
          v-text-field(type="number" label="PC (X Axis)" min="1" max="6" outline v-model="pcXval")
        v-flex(px-2)
          v-text-field(type="number" label="PC (Y Axis)" min="1" max="6" outline v-model="pcYval")
</template>
