const rowMenuOptions = [
  'sample',
  'header',
  'metadata',
  'masked',
];
const defaultRowOption = 'sample';
const rowPrimaryKey = 'header';

const colMenuOptions = [
  'key',
  'metadata',
  'measurement',
  'masked',
];
const defaultColOption = 'measurement';
const colPrimaryKey = 'key';

const normalize_methods = [
  // { label: 'None', value: null },
  { label: 'Min Max', value: 'normalize', priority: 10 },
];

const scaling_methods = [
  // { label: 'None', value: null },
  { label: 'Autoscaling', value: 'auto_scaling', priority: 200 },
  { label: 'Pareto Scaling', value: 'pareto_scaling', priority: 201 },
  { label: 'Range Scaling', value: 'range_scaling', priority: 202 },
  { label: 'Vast Scaling', value: 'vast_scaling', priority: 203 },
];

const transform_methods = [
  // { label: 'None', value: null },
  { label: 'Log 2', value: 'log_2', priority: 100 },
  { label: 'Log 10', value: 'log_10', priority: 101 },
  { label: 'Cube Root', value: 'cube_root', priority: 102 },
];

export {
  rowMenuOptions,
  defaultRowOption,
  rowPrimaryKey,

  colMenuOptions,
  defaultColOption,
  colPrimaryKey,

  normalize_methods,
  scaling_methods,
  transform_methods,
};
