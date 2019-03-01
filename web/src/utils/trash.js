/**
 * This file is for code I don't think should exist.
 * Mostly for things temporarily implemented in the client
 * that belong on the server (maybe)?
 */
import papa from 'papaparse';

function convertCsvToRows(csvstring) {
  return papa.parse(csvstring);
}

export {
  convertCsvToRows,
}
