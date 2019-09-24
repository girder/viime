import papa from 'papaparse';
import { validationMeta } from './constants';
import RangeList from './rangelist';
import SessionStore from './sessionStore';

/**
 * A function to group an array of objects
 * by a given key
 * https://stackoverflow.com/questions/14446511/most-efficient-method-to-groupby-on-a-array-of-objects
 */
function groupBy(xs, key) {
  return xs.reduce((rv, x) => {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
}

/**
 * Convert decimal to base26 in upper case
 * where A = 1, Z = 26, AA = 27, and 0 cannot be encoded.
 * @param {Number} dec a decimal number to convert
 */
function base26Converter(dec) {
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

function convertCsvToRows(csvstring) {
  if (!csvstring) {
    return { data: [] };
  }
  const { data } = papa.parse(csvstring);
  return { data: data.slice(0, data.length - 1) };
}

/**
 * A function to clean up server validation messages into
 * the schema this applicaiton expects.
 * @param {Array<Object>} errors raw response from api
 * @param {Array<Object} columns sorted response from api
 */
function mapValidationErrors(errors, columns) {
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
    const error = {
      severity,
      type,
      context,
      title,
      column_index,
      ...errorMeta,
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

export {
  base26Converter,
  convertCsvToRows,
  mapValidationErrors,
  RangeList,
  SessionStore,
};
