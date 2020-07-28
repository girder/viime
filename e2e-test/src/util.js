import { vBtn, vList } from 'jest-puppeteer-vuetify';

export const { CLIENT_URL } = process.env;

export async function deleteAllDatasets() {
  // firstUploadedItem returns a uploaded file node list
  const firstUploadedItem = await page.$x(vList({ content: 'upload-list theme--light' }));
  if (firstUploadedItem.length !== 0) {
    await expect(page).toClickXPath(vBtn('clear all'));
    await page.waitForXPath(vBtn('Delete'));
    await expect(page).toClickXPath(vBtn('Delete'));
  }
}

export async function allCleared() {
  const firstUploadedItem = await page.$x(vList({ content: 'upload-list theme--light' }));
  await expect(firstUploadedItem).toHaveLength(0);
}
