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
      validator: d => d === null || Array.isArray(d),
      required: true,
    },
  },

  data() {
    return {
      pcXval: '1',
      pcYval: '2',
      showCrosshairs: true,
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
vis-tile(title="PCA Loadings Plot")
  loadings-plot(
    :width="width",
    :height="height",
    :points="points",
    :pc-x="pcX",
    :pc-y="pcY",
    :show-crosshairs="showCrosshairs")
  template(v-slot:controls)
    v-card
      v-layout(column wrap)
        v-flex(px-2 pt-3)
          v-text-field(type="number" label="PC (X Axis)" min="1" max="6" outline v-model="pcXval")
        v-flex(px-2)
          v-text-field(type="number" label="PC (Y Axis)" min="1" max="6" outline v-model="pcYval")
        v-flex
          v-switch(v-model="showCrosshairs" label="Show crosshairs")
</template>
