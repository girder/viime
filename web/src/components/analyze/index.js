import WilcoxonTest from './WilcoxonTest.vue';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';

export default [
  {
    path: 'wilcoxon', // same as key
    name: 'Wilcoxon signed-rank test',
    shortName: 'Wilcoxon Test',
    description: 'The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.',
    component: WilcoxonTest,
    options: {
      zero_method: wilcoxon_zero_methods[0].value,
      alternative: wilcoxon_alternatives[0].value,
    },
  },
];
