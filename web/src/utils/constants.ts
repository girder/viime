import { IValidationMetaInfo } from '@/store/model';

const measurementColumnName = 'Metabolite';
const measurementValueName = 'Measurement';

const rowMenuOptions = [
  {
    value: 'header',
    icon: 'key',
    title: 'Header',
    color: 'accent',
    mutex: true,
  },
  {
    value: 'metadata',
    icon: 'metadata',
    title: 'Metadata',
    color: 'accent2',
    mutex: false,
  },
  {
    value: 'masked',
    icon: 'masked',
    title: 'Masked',
    color: 'secondary',
    mutex: false,
  },
  {
    value: 'sample',
    icon: null,
    title: 'Sample',
    color: null,
    mutex: false,
  },
];
const defaultRowOption = 'sample';
const rowFallbackType = 'metadata';
const rowPrimaryKey = 'header';

const colMenuOptions = [
  {
    value: 'key',
    icon: 'key',
    title: 'Primary Sample ID',
    color: 'primary',
    mutex: true,
  },
  {
    value: 'group',
    icon: 'group',
    title: 'Group',
    color: 'accent3',
    mutex: true,
  },
  {
    value: 'metadata',
    icon: 'metadata',
    title: 'Metadata',
    color: 'accent2',
    mutex: false,
  },
  {
    value: 'masked',
    icon: 'masked',
    title: 'Masked',
    color: 'secondary',
    mutex: false,
  },
  {
    value: 'measurement',
    icon: null,
    title: 'Metabolite',
    color: null,
    mutex: false,
  },
];
const defaultColOption = 'measurement';
const colFallbackType = 'metadata';
const colPrimaryKey = 'key';
const colGroupKey = 'group';

const mcar_imputation_methods = [
  {
    label: 'Random Forest',
    value: 'random-forest',
    helpText: `For each gene with missing values, this method finds the k nearest genes using Euclidean metric
  and imputes missing elements by averaging those non-missing elements of its neighbors.
  In metabolomics studies, we applied kNN to find k nearest samples instead and imputed the missing elements.
  We applied R package impute for this imputation approach.`,
  },
  {
    label: 'KNN',
    value: 'knn',
    helpText: `For each variable with missing values,
    we applied kNN to find k nearest samples and imputed the missing elements.
    We applied R package impute for this imputation approach.`,
  },
  {
    label: 'Mean',
    value: 'mean',
    helpText: 'This method replaces missing elements with an average value of non-missing elements in the corresponding variable.',
  },
  {
    label: 'Median',
    value: 'median',
    helpText: 'This method replaces missing elements with a median value of non-missing elements in the corresponding variable.',
  },
];
const mnar_imputation_methods = [
  {
    label: 'Zero',
    value: 'zero',
    helpText: 'This method replaces all missing elements with zero.',
  },
  {
    label: 'Half Minimum',
    value: 'half-minimum',
    helpText: 'This method replaces missing elements with half of the minimum of non-missing elements in the corresponding variable.',
  },
];

const normalize_methods = [
  { label: 'None', value: null, arg: null },
  { label: 'Min Max', value: 'minmax', arg: null },
  { label: 'Sum', value: 'sum', arg: null },
  { label: 'Reference Sample', value: 'reference-sample', arg: 'row.sample.name' },
  { label: 'Weight/Volume', value: 'weight-volume', arg: 'column.metadata.header' },
];

const scaling_methods = [
  { label: 'None', value: null },
  { label: 'Autoscaling', value: 'auto' },
  { label: 'Pareto Scaling', value: 'pareto' },
  { label: 'Range Scaling', value: 'range' },
  { label: 'Vast Scaling', value: 'vast' },
  { label: 'Level Scaling', value: 'level' },
];
const transform_methods = [
  { label: 'None', value: null },
  { label: 'Log 10', value: 'log10' },
  { label: 'Log 2', value: 'log2' },
  { label: 'Square Root', value: 'squareroot' },
  { label: 'Cube Root', value: 'cuberoot' },
];

const validationMeta: {[key: string]: IValidationMetaInfo} = {
  'group-missing': {
    // A static description string
    description: 'Select a column to contain group data',
    // Should the error be clickable?
    clickable: false,
    // Should the error be displayed as a list in another toolbar?
    multi: false,
  },
  'primary-key-missing': {
    description: 'Select a column to contain primary key data',
    clickable: false,
    multi: false,
  },
  'header-missing': {
    description: 'Select a row to contain header data',
    clickable: false,
    multi: false,
  },
  'invalid-primary-key': {
    description: 'Primary key is not valid',
    clickable: true,
    multi: false,
  },
  'invalid-group': {
    description: 'Group is not valid',
    clickable: true,
    multi: false,
  },
  'invalid-header': {
    description: 'Header is not valid',
    clickable: true,
    multi: false,
  },
  'low-variance': {
    description: 'Low column data variance',
    clickable: true,
    multi: true,
  },
  'missing-data': {
    description: 'All groups exceed 25% missing data',
    clickable: true,
    multi: true,
  },
  'non-numeric-data': {
    description: 'Table contains non-numeric metabolite data',
    clickable: false,
    multi: false,
  },
  'non-numeric-column': {
    description: 'A column contains non-numeric metabolite data',
    clickable: true,
    multi: true,
  },
  'non-numeric-row': {
    description: 'A row contains non-numeric metabolite data',
    clickable: true,
    multi: true,
  },
};

const plot_types = {
  TRANSFORM: 'transform',
  ANALYSIS: 'analysis',
};

const colors = {
  selected: '#ffa500',
  notSelected: '#c3c3c3',
  correlationNode: '#4682b4',
  positiveCorrelation: '#999999',
  negativeCorrelation: '#ef8a62',
  mnarMethod: '#80b1d3',
  mcarMethod: '#bc80bd',
};

export {
  rowMenuOptions,
  defaultRowOption,
  rowPrimaryKey,
  rowFallbackType,

  colMenuOptions,
  defaultColOption,
  colPrimaryKey,
  colGroupKey,
  colFallbackType,

  mcar_imputation_methods,
  mnar_imputation_methods,
  normalize_methods,
  scaling_methods,
  transform_methods,

  validationMeta,

  plot_types,
  colors,

  measurementColumnName,
  measurementValueName,
};
