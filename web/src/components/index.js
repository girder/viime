import WilcoxonPlotTile from './vis/WilcoxonPlotTile.vue';
// import AnovaTest from './AnovaTest.vue';
import { wilcoxon_zero_methods, wilcoxon_alternatives, plot_types } from '../utils/constants';

export const analyses = [
  {
    path: 'wilcoxon', // same as key
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
  // {
  //   path: 'anova', // same as key
  //   name: 'ANOVA',
  //   shortName: 'ANOVA',
  //   description: 'TODO R custom code',
  //   component: AnovaTest,
  //   options: {
  //   },
  // },
];
