import { vBtn, vList, vListTile } from 'jest-puppeteer-vuetify';

export const { CLIENT_URL } = process.env;

export async function deleteAllDatasets() {
  // $x returns a list of all elements matching an XPath
  const uploadedItems = await page.$x(vList(vListTile({ cssClass: 'theme--light' })));
  if (uploadedItems.length > 0) {
    await expect(page).toClickXPath(vBtn('clear all'));
    await page.waitForXPath(vBtn('Delete'));
    await expect(page).toClickXPath(vBtn('Delete'));
  }
}

export async function uploadDataset(datasetName) {
  const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
  const fileName = datasetName.concat('.csv');
  const datasetPath = '../e2e-test/data/';
  const filePath = datasetPath.concat(fileName);
  await fileInputElementHandle.uploadFile(filePath);
  await page.waitForXPath(vListTile({ title: fileName }));
}

/**
 * Opens the Analysis nav tab and clicks on the given analysis
 * @param {string} analysis
 */
export async function analyzeTable(analysis) {
  if ((await page.$x(`//div[contains(@class, "v-list__group__header--active")]/div${vListTile({ title: 'Analyze Table' })}`)).length === 0) {
    // only click on the Analyze Table nav item if it isn't open already
    await expect(page).toClickXPath(vListTile({ title: 'Analyze Table' }));
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  // click the desired analysis
  await expect(page).toClickXPath(vListTile({ title: analysis }));
  await new Promise((resolve) => setTimeout(resolve, 1000));
}
