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
    title: 'Primary Key',
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
    title: 'Measurement',
    color: null,
    mutex: false,
  },
];
const defaultColOption = 'measurement';
const colFallbackType = 'metadata';
const colPrimaryKey = 'key';
const colGroupKey = 'group';

const normalize_methods = [
  { label: 'Min Max', value: 'minmax', priority: 10 },
  { label: 'None', value: null },
];

const scaling_methods = [
  { label: 'Autoscaling', value: 'auto_scaling', priority: 200 },
  { label: 'Pareto Scaling', value: 'pareto_scaling', priority: 201 },
  { label: 'Range Scaling', value: 'range_scaling', priority: 202 },
  { label: 'Vast Scaling', value: 'vast_scaling', priority: 203 },
  { label: 'None', value: null },
];

const transform_methods = [
  { label: 'Log 2', value: 'log_2', priority: 100 },
  { label: 'Log 10', value: 'log_10', priority: 101 },
  { label: 'Cube Root', value: 'cube_root', priority: 102 },
  { label: 'None', value: null },
];

const validationMeta = {
  'group-missing': {
    description: 'Select a column to contain group data.',
    clickable: false,
  },
  'primary-key-missing': {
    description: 'Select a column to contain primary key data.',
    clickable: false,
  },
  'header-missing': {
    description: 'Select a row to contain header data.',
    clickable: false,
  },
  'invalid-primary-key': {
    description: 'Primary key is not valid',
    clickable: true,
  },
  'invalid-group': {
    description: 'Group is not valid',
    clickable: true,
  },
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

  normalize_methods,
  scaling_methods,
  transform_methods,

  validationMeta,
};
