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
    description: 'TODO R custom code',
    component: WilcoxonPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.metaboliteTable,
  },
  {
    path: 'anova',
    name: 'ANOVA',
    shortName: 'ANOVA',
    description: 'TODO R custom code',
    component: AnovaTableTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.metaboliteTable,
  },
  {
    path: 'heatmap',
    name: 'Heatmap',
    shortName: 'Heatmap',
    description: 'cool stuff',
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
    description: 'TODO',
    component: CorrelationTile,
    args: {
      min_correlation: 0.6,
      method: correlation_methods[0].value,
    },
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.graph,
  },
];
