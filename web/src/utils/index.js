import papa from 'papaparse';

import RangeList from './rangelist';
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
  const { data } = papa.parse(csvstring);
  return { data: data.slice(0, data.length - 1) };
}

export {
  base26Converter,
  convertCsvToRows,
  RangeList,
};
