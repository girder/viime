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
    maxComponents: {
      required: true,
      type: Number,
      validator: Number.isInteger,
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

  watch: {
    maxComponents(val) {
      const clamp = (text) => {
        let curVal = Number.parseInt(text, 10);
        if (curVal > val) {
          curVal = val;
        }

        return String(curVal);
      };

      this.pcXval = clamp(this.pcXval);
      this.pcYval = clamp(this.pcYval);
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
    v-menu(bottom, offset-y, left, :min-width="150", :close-on-content-click="false")
      template(v-slot:activator="{ on }")
        v-btn(v-on="on", icon)
          v-icon.mdi.mdi-dots-vertical

      v-card.pa-1(flat)
        v-layout(column)
          v-text-field.pa-2(
              hide-details,
              type="number",
              label="PC (X Axis)",
              min="1",
              :max="maxComponents",
              outline,
              v-model="pcXval")
          v-text-field.pa-2(
              hide-details,
              type="number",
              label="PC (Y Axis)",
              min="1",
              :max="maxComponents",
              outline,
              v-model="pcYval")
          v-switch.ma-2(hide-details, v-model="showCrosshairs", label="Show crosshairs")
</template>
