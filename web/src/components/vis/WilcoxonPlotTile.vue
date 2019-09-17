<script>
import WilcoxonPlot from '@/components/vis/WilcoxonPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import plotData from './mixins/plotData';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from '../../utils/constants';

export default {
  components: {
    WilcoxonPlot,
    VisTile,
  },

  mixins: [plotData('wilcoxon')],

  props: {
    width: {
      // required: true,
      default: 600,
      type: Number,
      validator: Number.isInteger,
    },
    height: {
      // required: true,
      default: 600,
      type: Number,
      validator: Number.isInteger,
    },
    id: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      zero_methods: wilcoxon_zero_methods,
      alternatives: wilcoxon_alternatives,
    };
  },
};
</script>

<template lang="pug">
vis-tile(title="Wilcoxon Test", :loading="plot.loading")
  wilcoxon-plot(
      :width="width",
      :height="height",
      :data="plot.data && plot.data.data",
      :indices="plot.data && plot.data.indices")
  //- template(v-slot:controls)
  //-   toolbar-option(title="Zero Methods", :value="options.zero_method",
  //-       :options="zero_methods",
  //-       @change="changeOption({zero_method: $event})")
  //-   toolbar-option(title="Alternatives", :value="options.alternative",
  //-       :options="alternatives",
  //-       @change="changeOption({alternative: $event})")
</template>
