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
  { label: 'Random Forest', value: 'random-forest' },
  { label: 'KNN', value: 'knn' },
  { label: 'Mean', value: 'mean' },
  { label: 'Median', value: 'median' },
];
const mnar_imputation_methods = [
  { label: 'Zero', value: 'zero' },
  { label: 'Half Minimum', value: 'half-minimum' },
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
  { label: 'Square Root', value: 'squareroot' },
  { label: 'Cube Root', value: 'cuberoot' },
];

const validationMeta = {
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
};

const plot_types = {
  TRANSFORM: 'transform',
  ANALYSIS: 'analysis',
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
};
