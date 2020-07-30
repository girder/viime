import {
  vBtn,
  vListTile,
  vIcon,
} from 'jest-puppeteer-vuetify';
import { CLIENT_URL } from '../util';


describe('relabel dataset', () => {
  it('make dataset ready for analysis with 2 clicks', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/cleanUpTest.csv');
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv ', content: 'Dataset processed with 1 validation failures' }));

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest.csv ', content: 'Dataset processed with 1 validation failures' }) + vBtn('View Data'));

    //  verify the dataset is failing
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // select the third column(column 'C') and mark it as a 'Group'
    await expect(page).toClickXPath("//div[@class='column-header-cell type-measurement'][contains(text(), 'C')]");
    await expect(page).toClickXPath("//input[@value='group']");

    //  verify the dataset is ready to process but needs to be more explict
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });

  it('mask all and unmask', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/cleanUpTest1.csv');
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv ', content: 'Dataset processed with 1 validation failures' }));

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest1.csv ', content: 'Dataset processed with 1 validation failures' }) + vBtn('View Data'));

    //  verify the dataset is failing
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // verify the dataset gets an error
    await expect(page).toClickXPath(vListTile({ title: 'Non-numeric column' }));

    // click 'mask all' to fix it
    await expect(page).toClickXPath(vBtn('Mask all'));

    //  verify the dataset is ready to process again
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // verify the column is masked and then click on the masked column
    await expect(page).toClickXPath("//div[@class='column-header-cell type-masked mdi mdi-eye-off']");

    // select the masked column and mark it as a 'Group'
    await expect(page).toClickXPath("//input[@value='group']");

    //  verify the dataset is ready to process again
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });

  it('fix selecting wrong data type for file name', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/cleanUpTest2.csv');
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv ', content: 'Dataset processed with 1 validation failures' }));

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest2.csv ', content: 'Dataset processed with 1 validation failures' }) + vBtn('View Data'));

    //  verify the dataset is failing
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // select the third column(column 'C') and mark it as a 'Group'
    await expect(page).toClickXPath("//div[@class='column-header-cell type-measurement'][contains(text(), 'C')]");
    await expect(page).toClickXPath("//input[@value='group']");

    //  verify the dataset is ready to process
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // select file name column and click 'Metabolite' button while it should have been metadata
    await expect(page).toClickXPath("//div[@class='cell type-header']//div[contains(text(), 'File Name')]");
    await expect(page).toClickXPath("//input[@value='measurement']");

    // verify the dataset gets an error
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // Fixing the select file name column again and click 'Metadata' button
    await expect(page).toClickXPath("//div[@class='cell type-header']//div[contains(text(), 'File Name')]");
    await expect(page).toClickXPath("//span[contains(text(), 'Metadata')]");

    //  verify the dataset is ready to process again
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });
});
