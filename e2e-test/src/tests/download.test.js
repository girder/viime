import { vBtn, vListTile } from 'jest-puppeteer-vuetify';
import { uploadDataset } from '../util';


describe('download dataset', () => {
  it('select and unselect filters', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('downloadTest');
    await expect(page).toClickXPath(vListTile({ title: 'downloadTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click analyze table
    await expect(page).toClickXPath(vListTile({ title: 'Analyze Table' }));

    // click ANOVA
    await expect(page).toClickXPath(vListTile({ title: 'ANOVA' }));

    // select 7 rows: Alanine, Glutamine, Nicotinurate, Sarcosine, Aspartate, Glucose, Glutathione
    /* eslint prefer-template: "off" */
    await expect(page).toClickXPath("//*[text()='C26 - C26.Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    await expect(page).toClickXPath("//*[text()='C26 - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    await expect(page).toClickXPath("//*[text()='C26 - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));

    // click download data
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // unselect 'Selected' for Metabolite Filter
    await expect(page).toClickXPath("//div[label[contains(.,'Selected (7')]]//input");

    // verify 24 columns has unselected
    await page.waitForXPath("//div[@class='column-header']/div[@class='column-header-cell'][contains(text(), '20 x 17')]");

    // unselect 'C26' for Sample Filter
    await expect(page).toClickXPath("//div[label[contains(.,'C26 (5)')]]//input");

    // verify 5 rows are unselected
    await page.waitForXPath("//div[@class='column-header']/div[@class='column-header-cell'][contains(text(), '15 x 17')]");

    // select Transpose Table
    await expect(page).toClickXPath("//label[text()='Transpose Table']");

    //  verify it is selected
    await page.waitForXPath("//div[@class='column-header']/div[@class='column-header-cell'][contains(text(), '17 x 15')]");
  });

  // TODO: implement code to allow download action in headless mode
  it('download a data set', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('downloadTest');
    await expect(page).toClickXPath(vListTile({ title: 'downloadTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click analyze table
    await expect(page).toClickXPath(vListTile({ title: 'Analyze Table' }));

    // click ANOVA
    await expect(page).toClickXPath(vListTile({ title: 'ANOVA' }));

    // select 7 rows: Alanine, Glutamine, Nicotinurate, Sarcosine, Aspartate, Glucose, Glutathione
    /* eslint prefer-template: "off" */
    await expect(page).toClickXPath("//*[text()='C26 - C26.Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    await expect(page).toClickXPath("//*[text()='C26 - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    await expect(page).toClickXPath("//*[text()='C26 - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));

    // click download data
    await expect(page).toClickXPath(vListTile({ title: 'Download Data' }));

    // this download action won't work
    await expect(page).toClickXPath(vBtn({ content: 'Metabolite List' }));
  });
});
//
