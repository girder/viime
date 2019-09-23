import WilcoxonPlotTile from './WilcoxonPlotTile.vue';
import AnovaTableTile from './AnovaTableTile.vue';
import CorrelationTile from './CorrelationTile.vue';
import { wilcoxon_zero_methods, wilcoxon_alternatives, plot_types } from '../../utils/constants';

export default [
  {
    path: 'wilcoxon',
    name: 'Wilcoxon signed-rank test',
    shortName: 'Wilcoxon Test',
    description: 'The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.',
    component: WilcoxonPlotTile,
    args: {
      zero_method: wilcoxon_zero_methods[0].value,
      alternative: wilcoxon_alternatives[0].value,
    },
    type: plot_types.ANALYSIS,
    help: 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html',
  },
  {
    path: 'anova',
    name: 'ANOVA',
    shortName: 'ANOVA',
    description: 'TODO R custom code',
    component: AnovaTableTile,
    options: {},
    type: plot_types.ANALYSIS,
  },
  {
    path: 'correlation',
    name: 'Correlation Network',
    shortName: 'Correlation',
    description: 'TODO',
    component: CorrelationTile,
    args: {
      min_correlation: 0.3,
      linkDistance: 50,
      filteredGroups: [],
      nodeColor: null, // null use the first one
    },
    type: plot_types.ANALYSIS,
  },
];
