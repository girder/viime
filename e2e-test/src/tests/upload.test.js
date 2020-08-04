import { vBtn, vListTile } from 'jest-puppeteer-vuetify';


describe('upload dataset', () => {
  it('upload one dataset', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/uploadTest.csv');
    await page.waitForXPath(vListTile({ title: 'uploadTest.csv ' }));
    await page.waitForXPath(vListTile({ title: 'uploadTest.csv ', content: 'Dataset processed with 1 validation failures' }));
  });
  it('upload 3 dataset', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");

    await fileInputElementHandle.uploadFile('../e2e-test/data/uploadTest1.csv');
    await page.waitForXPath(vListTile({ title: 'uploadTest1.csv ' }));
    await page.waitForXPath(vListTile({ title: 'uploadTest1.csv ', content: 'Dataset processed with 1 validation failures' }));

    await fileInputElementHandle.uploadFile('../e2e-test/data/uploadTest2.csv');
    await page.waitForXPath(vListTile({ title: 'uploadTest2.csv ' }));
    await page.waitForXPath(vListTile({ title: 'uploadTest2.csv ', content: 'Dataset processed with 1 validation failures' }));

    await fileInputElementHandle.uploadFile('../e2e-test/data/uploadTest3.csv');
    await page.waitForXPath(vListTile({ title: 'uploadTest3.csv ' }));
    await page.waitForXPath(vListTile({ title: 'uploadTest3.csv ', content: 'Dataset processed with 1 validation failures' }));
  });
});
