/**
 * This file is for code I don't think should exist.
 * Mostly for things temporarily implemented in the client
 * that belong on the server (maybe)?
 */
import papa from 'papaparse';

function convertCsvToRows(csvstring) {
  const { data } = papa.parse(csvstring);
  return { data: data.slice(0, data.length - 1) };
}

export {
  convertCsvToRows,
};
