
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
}
