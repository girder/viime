
export interface IValidationMetaInfo {
  description: string;
  clickable: boolean;
  multi: boolean;
}

export interface IValidationError extends IValidationMetaInfo {
  severity: boolean;
  type: string;
  context: string;
  title: string;
  column_index: number;
  data: { index: number, info: any, name: string }[]
}

export interface ITableColumn {
  column_index: number;
  column_header: string;
}

export interface ILevel {
  name: string;
  label?: string;
  description?: string;
  color: string;
}

export interface IMetaData {
  subtype: string | null;
  [key: string]: any;
  levels?: ILevel[];
}

export interface IDataFrame<T> {
  columnNames: string[];
  columnMetaData: IMetaData[];
  rowNames: string[];
  rowMetaData: IMetaData[];
  data: T[][];
}

export interface IDataSet {
  id: string;
  name: string;
  groupLevels: ILevel[];
  selectedColumns: string[];
  validatedMeasurements: IDataFrame<number>;
  validatedMeasurementsMetaData: IDataFrame<string | number>;
  validatedSampleMetaData: IDataFrame<string | number>;
  validatedGroups: IDataFrame<string>;

  validation: IValidationError[];
}

export interface ISampleFile {
  id: string;
  name: string;
  description?: string;
}

export interface ISampleGroup {
  name: string;
  description?: string;

  files: ISampleFile[];
}
