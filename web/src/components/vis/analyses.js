import WilcoxonPlotTile from './WilcoxonPlotTile.vue';
import WilcoxonVolcanoPlotTile from './WilcoxonVolcanoPlotTile.vue';
import AnovaTableTile from './AnovaTableTile.vue';
import AnovaVolcanoPlotTile from './AnovaVolcanoPlotTile.vue';
import HeatmapTile from './HeatmapTile.vue';
import CorrelationTile from './CorrelationTile.vue';
import PcaPage from './PcaPage/PcaPage.vue';
import BoxPlotLargeTile from './BoxPlotLargeTile.vue';
import GroupPredictionTile from './GroupPredictionTile.vue';
import { plot_types } from '../../utils/constants';
import { correlation_methods } from './constants';
import vuetify from '../../utils/vuetifyConfig';

const analysisList = [
  {
    path: 'pcapage',
    name: 'Principal Component Analysis',
    shortName: 'PCA',
    description() {
      return (<div>
        <p>Principal Component Analysis (PCA) is a method of dimensionality
        reduction to obtain the maximum variance in the fewest number of
          uncorrelated variables called principal components.</p>

        <p>PCA is a projection based method which transforms the data by
          projecting it onto a set of orthogonal axes.</p>
      </div>);
    },
    component: PcaPage,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.pca,
  },
  {
    path: 'boxplot',
    name: 'Boxplots',
    shortName: 'Boxplots',
    description() {
      return (<div>
        <p>
          This chart shows the distribution of each metabolite's measurements
          using a series of box plots.
        </p>
        <p>Each metabolite appears along the y-axis, with a horizontal box plot showing
          the four quartile values, emphasizing
          the interquartile range (IQR) with solid bars. Individual outliers appear as well:
          normal ones, falling at
          least 1.5 IQRs away from the interquartile range, as dots; and "far-out" outliers,
          falling at least 3 IQRs away from the interquartile range, as larger dots.
        </p>
        <p>
          Hovering the mouse pointer over various parts of the plot will show detailed
          information in a tooltip.
          These include details of the different quartile ranges, and the values of outliers.
        </p>
      </div>);
    },
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
    description() {
      return (<div>
        <p>Non-parametric test to compare two groups.</p>
        <p>
          <strong>Bonferoni</strong>:
          It is a correction of multiple comparisons for independent statistical test
          made simultaneously.
          (It sets the critical p-value as <code>alpha/n</code>,
          where n is the number of tests and alpha is the probability of rejecting the
          null hypothesis when it is true, also called type I error rate).
        </p>
        <p>
          <strong>Hochberg</strong>:
          It is a correction of multiple comparisons for independent statistical test made
          simultaneously. (It sets the critical value as <code>(i/m)Q</code> where i is the
          rank of the
          p-values when ordered
          from smallest to largest, m is the number of tests and Q is the false discovery rate)
        </p>
      </div>);
    },
    component: WilcoxonPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.metaboliteTable,
  },
  {
    path: 'wilcoxon_volcano',
    name: 'Wilcoxon test (Volcano Plot)',
    shortName: 'Wilcoxon Volcano Plot',
    description() {
      return (<div>
        <p>Non-parametric test to compare two groups.</p>
      </div>);
    },
    component: WilcoxonVolcanoPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.pca,
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
    path: 'anova_volcano',
    name: 'ANOVA (Volcano Plot)',
    shortName: 'ANOVA Volcano Plot',
    description: 'Test to compare 3 or more groups assuming normal distribution, the group pairwise comparisons are adjusted with Tukey HSD',
    component: AnovaVolcanoPlotTile,
    args: {},
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.pca,
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
    description() {
      return (<div>
        <p>An interactive node-link display of the pairwise correlation between
        variables.</p>

        <p>Thicker links represent stronger correlations. Gray means positive
        correlation, while orange means negative.</p>

        <p>You can hover your mouse over a node to see what metabolite it
        represents, and hovering over a link will show the correlation value
        between the two metabolites it connects.</p>

        <p>You can click and drag on nodes to move them around. This allows you
        to, e.g., visually isolate clusters of correlated variables. Click again on
        a node to unpin it.</p>

        <p>To only display part of the network, use the search controls on the left.
        You can manually add to the searched metabolites by holding shift and
        clicking on a node.</p>
      </div>);
    },
    component: CorrelationTile,
    args: {
      min_correlation: 0.6,
      method: correlation_methods[0].value,
    },
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.graph,
  },
  {
    path: 'roc',
    name: 'Group Prediction',
    shortName: 'Group Prediction',
    description() {
      return (<div>
        <p>This analysis uses the receiver operating characteristic (ROC) curve
          and area under the curve (AUC) for prediction of group membership
          using either logistic regression or random forest methods.</p>
      </div>);
    },
    component: GroupPredictionTile,
    args: {
      columns: null,
      group1: null,
      group2: null,
      method: 'random_forest',
    },
    type: plot_types.ANALYSIS,
    icon: vuetify.icons.pca,
  },
];

// Create a path-indexable map version of the analysis list.
const analysisMap = Object.freeze(analysisList.reduce((map, entry) => ({
  ...map,
  [entry.path]: entry,
}), {}));

export default analysisList;
export {
  analysisMap,
};
