import {
  vBtn,
  vCard,
  vIcon,
  vListTile,
  vList,
} from 'jest-puppeteer-vuetify';
import { deleteAllDatasets, uploadDataset } from '../util';


describe('delete dataset', () => {
  it('delete one dataset', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await deleteAllDatasets();

    await uploadDataset('deleteTest');
    await page.waitForXPath(vListTile({ title: 'deleteTest.csv ', content: 'Dataset ready for analysis' }));

    // wait for data set to be uploaded and then delete
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath(vBtn(vIcon('mdi-close')));
    await page.waitForXPath(vCard({ headline: 'Really delete 1 dataset?' }));
    await expect(page).toClickXPath(vBtn('Delete'));

    // wait for the data set to be deleted then verify
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).not.toContainXPath(vListTile({ title: 'deleteTest.csv ' }));
  });

  it('clear all', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await deleteAllDatasets();

    await uploadDataset('deleteTest1');
    await page.waitForXPath(vListTile({ title: 'deleteTest1.csv ', content: 'Dataset ready for analysis' }));

    await uploadDataset('deleteTest2');
    await page.waitForXPath(vListTile({ title: 'deleteTest2.csv ', content: 'Dataset processed with 1 validation failures' }));

    await uploadDataset('deleteTest3');
    await page.waitForXPath(vListTile({ title: 'deleteTest3.csv ', content: 'Dataset processed with 1 validation failures' }));

    // wait for data sets to be all uploaded before deletion
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath(vBtn('clear all'));
    await page.waitForXPath(vCard({ headline: 'Really delete 3 datasets?' }));
    await expect(page).toClickXPath(vBtn('Delete'));

    // wait to make sure uploaded datasets are all cleared then verify
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const uploadedItems = await page.$x(vList(vListTile({ cssClass: 'theme--light' })));
    await expect(uploadedItems).toHaveLength(0);
  });
});
