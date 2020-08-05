import { vBtn, vListTile } from 'jest-puppeteer-vuetify';
import { uploadDataset } from '../util';


describe('download dataset', () => {
  it('transform table', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('tableTest');
    await expect(page).toClickXPath(vListTile({ title: 'tableTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click transform table
    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change normalize to 'Min Max'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Min Max')]");
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // verify the value has been changed: hard coded but there might be a better way to do that
    await page.waitForXPath("//div[@class='vue-recycle-scroller__item-view'][1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.249')]");
    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change transform to 'log 10'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Log 10')]");

    // click download data to verify the change
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));
    await page.waitForXPath("//div[@class='vue-recycle-scroller__item-view'][1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '-0.603')]");

    await expect(page).toClickXPath(vListTile({ title: 'Transform Table' }));

    // change scale to 'Pareto Scaling'
    await expect(page).toClickXPath("//label[@class='v-label theme--light'][contains(text(), 'Pareto Scaling')]");
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));
    await page.waitForXPath("//div[@class='vue-recycle-scroller__item-view'][1]//div[@class='column']/div[@class='cell type-sample'][1][contains(text(), '0.393')]");
  });
  it('analyze table and select matabolite', async () => {
    let selectedMetabolites;
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('tableTest');
    await expect(page).toClickXPath(vListTile({ title: 'tableTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click analyze table
    await expect(page).toClickXPath(vListTile({ title: 'Analyze Table' }));

    // click ANOVA
    await expect(page).toClickXPath(vListTile({ title: 'ANOVA' }));

    // select some metabolites from ANOVA by adding the highlighted Metabolites to the selected set
    /* eslint prefer-template: "off" */
    await expect(page).toClickXPath("//*[text()='C26 - C26.Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(1);

    await expect(page).toClickXPath("//*[text()='C26 - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(4);

    await expect(page).toClickXPath("//*[text()='C26 - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(7);

    await expect(page).toClickXPath("//*[text()='C26.Fol - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(8);

    await expect(page).toClickXPath("//*[text()='C26.Fol - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(11);

    await expect(page).toClickXPath("//*[text()='Fol - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    await expect(selectedMetabolites).toHaveLength(12);
  });
  it('select and unselect filters', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('tableTest');
    await expect(page).toClickXPath(vListTile({ title: 'tableTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click download data
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // unselect 'Selected' for Metabolite Filter
    await expect(page).toClickXPath("//input[@aria-checked='true'][@aria-label='Selected (0)']");

    // verify unselected
    await page.waitForXPath("//input[@aria-checked='false'][@aria-label='Selected (0)']");

    // unselect 'C26' for Sample Filter
    await expect(page).toClickXPath("//input[@aria-checked='true'][@aria-label='C26 (5)']");

    // verify unselected
    await page.waitForXPath("//input[@aria-checked='false'][@aria-label='C26 (5)']");

    // verify that 'Transpose Table' is not selected yet
    await expect(page).not.toContainXPath("//input[@aria-checked='true'][@aria-label='Transpose Table']");

    // select Transpose Table
    await expect(page).toClickXPath("//label[text()='Transpose Table']");

    //  verify it is selected
    await expect(page).toContainXPath("//input[@aria-checked='true'][@aria-label='Transpose Table']");
  });
});
