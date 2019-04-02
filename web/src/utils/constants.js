const rowMenuOptions = [
  {
    value: 'header',
    icon: 'key',
    title: 'Header',
    color: 'light-green',
  },
  {
    value: 'metadata',
    icon: 'metadata',
    title: 'Metadata',
    color: 'purple',
  },
  {
    value: 'masked',
    icon: 'masked',
    title: 'Masked',
    color: 'grey',
  },
  {
    value: 'sample',
    icon: null,
    title: 'Sample',
    color: null,
  },
];
const defaultRowOption = 'sample';
const rowPrimaryKey = 'header';

const colMenuOptions = [
  {
    value: 'key',
    icon: 'key',
    title: 'Primary Key',
    color: 'blue-grey',
  },
  {
    value: 'group',
    icon: 'group',
    title: 'Group',
    color: 'pink',
  },
  {
    value: 'metadata',
    icon: 'metadata',
    title: 'Metadata',
    color: 'purple',
  },
  {
    value: 'masked',
    icon: 'masked',
    title: 'Masked',
    color: 'grey',
  },
  {
    value: 'measurement',
    icon: null,
    title: 'Measurement',
    color: null,
  },
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
