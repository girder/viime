import WilcoxonPlotTile from './WilcoxonPlotTile.vue';
import AnovaTableTile from './AnovaTableTile.vue';
import HeatmapTile from './HeatmapTile.vue';
import CorrelationTile from './CorrelationTile.vue';
import PcaPage from './PcaPage/PcaPage.vue';
import BoxPlotLargeTile from './BoxPlotLargeTile.vue';
import { plot_types } from '../../utils/constants';
import { correlation_methods } from './constants';
import vuetify from '../../utils/vuetifyConfig';

export default [
  {
    path: 'pcapage',
    name: 'Principal Component Analysis',
    shortName: 'PCA',
    description: 'TODO',
    component: PcaPage,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.pca,
  },
  {
    path: 'boxplot',
    name: 'Boxplots',
    shortName: 'Boxplots',
    description: 'show me the boxplots!',
    component: BoxPlotLargeTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.boxplot,
    iconStyle: {
      transform: 'rotate(90deg)scale(-1,1)',
    },
  },
  {
    path: 'wilcoxon',
    name: 'Wilcoxon test',
    shortName: 'Wilcoxon Test',
    description: ' Non-parametric test to compare two groups',
    component: WilcoxonPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.metaboliteTable,
  },
  {
    path: 'anova',
    name: 'ANOVA',
    shortName: 'ANOVA',
    description: 'Test to compare 3 or more groups assuming normal distribution, the group pairwise comparisons are adjusted with Tukey HSD',
    component: AnovaTableTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.metaboliteTable,
  },
  {
    path: 'heatmap',
    name: 'Heatmap',
    shortName: 'Heatmap',
    description: 'Is a graphical representation of the concentration differences between variables and samples',
    component: HeatmapTile,
    args: {
      column: null,
      column_filter: null,
      row: null,
      row_filter: null,
    },
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.heatmap,
  },
  {
    path: 'correlation',
    name: 'Correlation Network',
    shortName: 'Correlation Network',
    description: `Is a graphical representation of the pairwise correlations between variables.
    The different colors of the connections show the direction of the correlation and the wider
    the connection, the stronger the correlation`,
    component: CorrelationTile,
    args: {
      min_correlation: 0.6,
      method: correlation_methods[0].value,
    },
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.graph,
  },
];
