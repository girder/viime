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
  'group',
  'metadata',
  'measurement',
  'masked',
];
const defaultColOption = 'measurement';
const colPrimaryKey = 'key';

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
