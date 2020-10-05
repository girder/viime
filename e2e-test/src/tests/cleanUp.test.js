import {
  vBtn,
  vListTile,
  vIcon,
} from 'jest-puppeteer-vuetify';
import { uploadDataset } from '../util';


describe('relabel dataset', () => {
  it('mark as group', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('cleanUpTest');

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest.csv ', content: 'Dataset ready for analysis' }) + vBtn('View Data'));

    //  verify the dataset is ready to process
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // select the third column(column 'C', currently masked) and mark it as a 'Metabolite'
    await expect(page).toClickXPath("//div[contains(@class,'column-header-cell type-masked mdi mdi-eye-off')]");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath("//input[@value='measurement']");

    //  verify the dataset is failing
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // select the third column(column 'C') and mark it as a 'Group'
    await expect(page).toClickXPath("//div[contains(@class,'column-header-cell type-measurement')][contains(text(), 'C')]");
    await expect(page).toClickXPath("//input[@value='group']");

    //  verify the dataset is ready to process
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });

  it('mask all and unmask', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('cleanUpTest1');

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest1.csv ', content: 'Dataset ready for analysis' }) + vBtn('View Data'));

    //  verify the dataset is ready to process
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // select the third column(column 'C', currently masked) and mark it as a 'Metabolite'
    await expect(page).toClickXPath("//div[contains(@class,'column-header-cell type-masked mdi mdi-eye-off')]");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath("//input[@value='measurement']");

    //  verify the dataset is failing
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // click the error message to get fix recommendations
    await expect(page).toClickXPath(vListTile({ title: 'Non-numeric column' }));

    // click 'mask all' to fix it
    await expect(page).toClickXPath(vBtn('Mask all'));

    //  verify the dataset is ready to process again
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // verify the column is masked and then click on the masked column
    await expect(page).toClickXPath("//div[contains(@class,'column-header-cell type-masked mdi mdi-eye-off')]");

    // select the masked column and mark it as a 'Group'
    await expect(page).toClickXPath("//input[@value='group']");

    //  verify the dataset is ready to process again
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest1.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });

  it('mark as metabolite + metadata', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('cleanUpTest2');

    await expect(page).toClickXPath(vListTile({ title: 'cleanUpTest2.csv ', content: 'Dataset ready for analysis' }) + vBtn('View Data'));

    //  verify the dataset is ready to process
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));

    // select file name column and change it from Group to Metadata
    await expect(page).toClickXPath("//div[@class='cell type-header']//div[contains(text(), 'File Name')]");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath("//input[@value='metadata']");

    // verify the dataset gets an error because there is no Group column
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-alert theme--light warning--text' }));

    // Fixing the select treatment column and click 'Group' button
    await expect(page).toClickXPath("//div[@class='cell type-header']//div[contains(text(), 'Treatment')]");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath("//span[contains(text(), 'Group')]");

    //  verify the dataset is ready to process again
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page.waitForXPath(vListTile({ title: 'cleanUpTest2.csv' }) + vIcon({ cssClass: 'mdi mdi-check theme--light success--text' }));
  });
});
