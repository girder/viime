import Wilcoxon from './Wilcoxon.vue';
import Anova from './Anova.vue';
import { wilcoxon_zero_methods, wilcoxon_alternatives } from './constants';

export default [
  {
    path: 'wilcoxon', // same as key
    name: 'Wilcoxon signed-rank test',
    shortName: 'Wilcoxon Test',
    description: 'The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution. In particular, it tests whether the distribution of the differences x - y is symmetric about zero. It is a non-parametric version of the paired T-test.',
    component: Wilcoxon,
    options: {
      zero_method: wilcoxon_zero_methods[0].value,
      alternative: wilcoxon_alternatives[0].value,
    },
    help: 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html',
  },
  {
    path: 'anova', // same as key
    name: 'ANOVA',
    shortName: 'ANOVA',
    description: 'The one-way ANOVA tests the null hypothesis that two or more groups have the same population mean. The test is applied to samples from two or more groups, possibly with differing sizes.',
    component: Anova,
    options: {
    },
    help: 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html',
  },
];
