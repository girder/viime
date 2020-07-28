import { vBtn } from 'jest-puppeteer-vuetify';
import { CLIENT_URL } from '../util';


describe('upload dataset', () => {
  it('upload one dataset and verify it', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/Cancer chemo muscle (NMR).csv');
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_muscle_NMR.csv ')]");
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_muscle_NMR.csv ')]//following::span[contains(text(),'Dataset processed with 1 validation failures')]");
  });
  it('upload 3 dataset and verify it', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");

    await fileInputElementHandle.uploadFile('../e2e-test/data/Cancer chemo muscle (NMR).csv');
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_muscle_NMR.csv ')]");
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_muscle_NMR.csv ')]//following::span[contains(text(),'Dataset processed with 1 validation failures')]");

    await fileInputElementHandle.uploadFile('../e2e-test/data/Cancer chemo liver (NMR).csv');
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_liver_NMR.csv ')]");
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_liver_NMR.csv ')]//following::span[contains(text(),'Dataset ready for analysis')]");

    await fileInputElementHandle.uploadFile('../e2e-test/data/Cancer chemo serum (NMR).csv');
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_serum_NMR.csv ')]");
    await page.waitForXPath("//div[@class='v-list__tile__title'][contains(text(),'Cancer_chemo_serum_NMR.csv ')]//following::span[contains(text(),'Dataset processed with 1 validation failures')]");
  });
});
