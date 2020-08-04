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
