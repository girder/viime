<script>
import WilcoxonPlot from '@/components/vis/WilcoxonPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from '../../utils/constants';

export default {
  components: {
    WilcoxonPlot,
    ToolbarOption,
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
vis-tile(title="Wilcoxon Test", :loading="plot.loading", expanded)
  template(#controls)
    toolbar-option(title="Zero Methods", :value="plot.args.zero_method",
        :options="zero_methods",
        @change="changePlotArgs({zero_method: $event})")
    toolbar-option(title="Alternatives", :value="plot.args.alternative",
        :options="alternatives",
        @change="changePlotArgs({alternative: $event})")
  v-container.grow-overflow.ma-0(grid-list-lg, fluid)
    wilcoxon-plot(
        :width="width",
        :height="height",
        :data="plot.data && plot.data.data",
        :indices="plot.data && plot.data.indices")
</template>
