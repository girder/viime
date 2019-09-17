<script>
import WilcoxonPlot from '@/components/vis/WilcoxonPlot.vue';
import VisTileLarge from '@/components/vis/VisTileLarge.vue';
import ToolbarOption from '../ToolbarOption.vue';
import plotData from './mixins/plotData';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from '../../utils/constants';

export default {
  components: {
    WilcoxonPlot,
    ToolbarOption,
    VisTileLarge,
  },

  mixins: [plotData('wilcoxon')],

  props: {
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
vis-tile-large(title="Wilcoxon Test", :loading="plot.loading", expanded)
  template(#controls)
    toolbar-option(title="Zero Methods", :value="plot.args.zero_method",
        :options="zero_methods",
        @change="changePlotArgs({zero_method: $event})")
    toolbar-option(title="Alternatives", :value="plot.args.alternative",
        :options="alternatives",
        @change="changePlotArgs({alternative: $event})")
  wilcoxon-plot(:data="plot.data")
</template>
