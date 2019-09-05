<script>
import VisPca from '@/components/vis/VisPca.vue';
import VisTile from '@/components/vis/VisTile.vue';

export default {
  components: {
    VisPca,
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
    },
    dataset: {
      required: true,
    },
  },

  data() {
    return {
      pcXval: "1",
      pcYval: "2",
    };
  },

  computed: {
    pcX() {
      return Number.parseInt(this.pcXval);
    },

    pcY() {
      return Number.parseInt(this.pcYval);
    },
  },
}

</script>

<template lang="pug">
vis-tile(title="PCA Score Plot")
  vis-pca(:width="width", :height="height", :raw-points="rawPoints", :dataset="dataset", :pc-x="pcX", :pc-y="pcY")
  template(v-slot:controls)
    v-card
      v-layout(column wrap)
        v-flex(px-2 pt-3)
          v-text-field(type="number" label="PC (X Axis)" min="1" max="6" outline v-model="pcXval")
        v-flex(px-2)
          v-text-field(type="number" label="PC (Y Axis)" min="1" max="6" outline v-model="pcYval")
</template>
