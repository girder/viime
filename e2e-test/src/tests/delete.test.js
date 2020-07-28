import {
  vBtn,
  vCard,
  vIcon,
  vListTile,
} from 'jest-puppeteer-vuetify';
import { CLIENT_URL, deleteAllDatasets, allCleared } from '../util';


describe('delete dataset', () => {
  it('delete one dataset', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await deleteAllDatasets();

    // todo: make a function for upload file(s)
    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");
    await fileInputElementHandle.uploadFile('../e2e-test/data/deleteTest.csv');
    await page.waitForXPath(vListTile({ title: 'deleteTest.csv ' }));
    await page.waitForXPath(vListTile({ title: 'deleteTest.csv ', content: 'Dataset ready for analysis' }));

    await expect(page).toClickXPath(vBtn(vIcon('mdi-close')));
    await page.waitForXPath(vCard({ headline: 'Really delete 1 dataset?' }));
    await expect(page).toClickXPath(vBtn('Delete'));

    const previouslyUploadedFile = await expect(page).toContainXPath(vListTile({ title: 'deleteTest.csv ' }));
    await expect(previouslyUploadedFile).toBeUndefined();
  });

  it('clear all', async () => {
    await Promise.all([
      page.goto(CLIENT_URL),
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await deleteAllDatasets();

    const fileInputElementHandle = await page.waitForXPath("//input[@type='file']");

    // todo: make a function for upload file(s)
    await fileInputElementHandle.uploadFile('../e2e-test/data/deleteTest1.csv');
    await page.waitForXPath(vListTile({ title: 'deleteTest1.csv ' }));
    await page.waitForXPath(vListTile({ title: 'deleteTest1.csv ', content: 'Dataset ready for analysis' }));

    await fileInputElementHandle.uploadFile('../e2e-test/data/deleteTest2.csv');
    await page.waitForXPath(vListTile({ title: 'deleteTest2.csv ' }));
    await page.waitForXPath(vListTile({ title: 'deleteTest2.csv ', content: 'Dataset processed with 1 validation failures' }));

    await fileInputElementHandle.uploadFile('../e2e-test/data/deleteTest3.csv');
    await page.waitForXPath(vListTile({ title: 'deleteTest3.csv ' }));
    await page.waitForXPath(vListTile({ title: 'deleteTest3.csv ', content: 'Dataset processed with 1 validation failures' }));

    await expect(page).toClickXPath(vBtn('clear all'));

    await page.waitForXPath(vCard({ headline: 'Really delete 3 datasets?' }));
    await expect(page).toClickXPath(vBtn('Delete'));

    await allCleared();
  });
});
