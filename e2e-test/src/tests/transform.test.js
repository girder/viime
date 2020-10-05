import { vBtn, vListTile } from 'jest-puppeteer-vuetify';
import { uploadDataset } from '../util';


describe('transform table page', () => {
  it('transform table', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('transformTest');
    await expect(page).toClickXPath(vListTile({ title: 'transformTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click transform table
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change normalize to 'Min Max'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Min Max')]");
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // verify that the first two values in the first two columns of the table are correct
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.249')]");
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '0.137')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '1.000')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '0.356')]");
    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change transform to 'log 10'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Log 10')]");

    // click download data to verify the change
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // verify that the first two values in the first two columns of the table are correct
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '-0.603')]");
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '-0.863')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.000')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '-0.448')]");
    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change scale to 'Pareto Scaling'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Pareto Scaling')]");
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // verify that the first two values in the first two columns of the table are correct
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.393')]");
    await page.waitForXPath("//div[1]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '0.195')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.718')]");
    await page.waitForXPath("//div[2]//div[@class='column']/div[@class='cell type-sample'][2][contains(text(), '0.376')]");
  });
});
