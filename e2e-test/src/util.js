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
