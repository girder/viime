import papa from 'papaparse';
import { hsl } from 'd3-color';
import { validationMeta } from './constants';
import RangeList from './rangelist';
import SessionStore from './sessionStore';
import { ITableColumn, IDataFrame, IValidationError } from '@/store/model';

/**
 * A function to group an array of objects
 * by a given key
 * https://stackoverflow.com/questions/14446511/most-efficient-method-to-groupby-on-a-array-of-objects
 */
function groupBy<T>(xs: T[], key: keyof T) {
  return xs.reduce((rv, x) => {
    const v = x[key] as unknown as string;
    (rv[v] = rv[v] || []).push(x);
    return rv;
  }, {} as { [key: string]: T[]});
}

/**
 * Convert decimal to base26 in upper case
 * where A = 1, Z = 26, AA = 27, and 0 cannot be encoded.
 * @param {Number} dec a decimal number to convert
 */
function base26Converter(dec: number) {
  if (dec < 1) {
    throw new Error('Numbers below 1 cannot be encoded.');
  }
  let str = '';
  let acc = dec;
  while (acc > 0) {
    let val = acc % 26;
    if (val === 0) {
      val = 26; // Abnormal encoding: 1^26 is 'Z' because there's no 0.
    }
    acc = Math.floor((acc - val) / 26);
    str = String.fromCharCode(64 + val) + str;
  }
  return str;
}

function convertCsvToRows(csvstring: string) {
  if (!csvstring) {
    return { data: [] };
  }
  const { data } = papa.parse(csvstring);
  return { data: data.slice(0, data.length - 1) };
}

export interface IToSplitDictResult {
  columns?: string[];
  index?: string[];
  columnMetaData?: any[];
  rowMetaData?: any[];
  data: any[][];
}

function parsePandasDataFrame<T>(toSplitDictResult: IToSplitDictResult,
  baseDataFrame: IDataFrame<T>) {
  if (!toSplitDictResult) {
    return {
      columnNames: [],
      columnMetaData: [],
      rowNames: [],
      rowMetaData: [],
      data: [],
    };
  }

  const dummyMeta = (arr?: string[]) => {
    if (!arr) {
      return null;
    }
    return arr.map(() => ({ subtype: null }));
  };

  return {
    columnNames: toSplitDictResult.columns || baseDataFrame.columnNames,
    columnMetaData: dummyMeta(toSplitDictResult.columns) || baseDataFrame.columnMetaData,
    data: toSplitDictResult.data,
    rowNames: toSplitDictResult.index || baseDataFrame.rowNames,
    rowMetaData: dummyMeta(toSplitDictResult.index) || baseDataFrame.rowMetaData,
  };
}


/**
 * A function to clean up server validation messages into
 * the schema this applicaiton expects.
 * @param {Array<Object>} errors raw response from api
 * @param {Array<Object} columns sorted response from api
 */
function mapValidationErrors(errors: any[], columns: ITableColumn[]) {
  const grouped = groupBy(errors, 'type');
  const keys = Object.keys(grouped);
  return keys.map((errorType) => {
    const errorsOfType = grouped[errorType];
    const errorMeta = validationMeta[errorType];
    const {
      severity,
      type,
      context,
      title,
      column_index,
      data,
    } = errorsOfType[0];
    const error: IValidationError = {
      severity,
      type,
      context,
      title,
      column_index,
      ...errorMeta,
      data: [],
    };
    if (errorMeta.multi === true) {
      error.description = errorMeta.description;
      error.data = errorsOfType.map(e => ({
        index: e.column_index,
        info: e.data,
        name: columns[e.column_index].column_header,
      }));
    } else if (errorMeta.clickable === true) {
      error.title = `${title} in ${base26Converter(column_index + 1)}`;
    } else if (typeof data === 'string') {
      error.description = data;
    }
    return error;
  });
}

function textColor(backgroundColor: string | null) {
  if (!backgroundColor) {
    return 'black';
  }
  const c = hsl(backgroundColor);
  return c.l < 0.5 ? 'white' : 'black';
}

function formatter(v: string | number) {
  const nf = (n: number) => (n.toPrecision(6).length <= 10 ? n.toPrecision(6) : n.toExponential(4));
  return typeof v === 'number' || (v && !Number.isNaN(+v)) ? nf(typeof v === 'number' ? v : parseFloat(v)) : v;
}

// Adapted from https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
declare const opr: any;
declare const safari: any;
declare const InstallTrigger: any;

export function getBrowser() {
  const w: any = window;
  // Opera 8.0+
  // eslint-disable-next-line no-undef
  const isOpera = (!!w.opr && !!opr.addons) || !!w.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

  // Firefox 1.0+
  const isFirefox = typeof InstallTrigger !== 'undefined';

  // Safari 3.0+ "[object HTMLElementConstructor]"
  // eslint-disable-next-line wrap-iife,func-names,quotes,dot-notation,no-undef
  const isSafari = /constructor/i.test(w.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!w.safari || (typeof safari !== 'undefined' && safari.pushNotification));

  // Internet Explorer 6-11
  // eslint-disable-next-line spaced-comment
  const isIE = /*@cc_on!@*/false || !!(document as any).documentMode;

  // Edge 20+
  const isEdge = !isIE && !!w.StyleMedia;

  // Chrome 1 - 71
  const isChrome = !!w.chrome && (!!w.chrome.webstore || !!w.chrome.runtime);

  // Blink engine detection
  const isBlink = (isChrome || isOpera) && !!w.CSS;

  return {
    isOpera,
    isFirefox,
    isSafari,
    isIE,
    isEdge,
    isChrome,
    isBlink,
  };
}

export {
  base26Converter,
  convertCsvToRows,
  parsePandasDataFrame,
  mapValidationErrors,
  textColor,
  RangeList,
  SessionStore,
  formatter,
};
