import { vBtn, vListTile } from 'jest-puppeteer-vuetify';
import { uploadDataset } from '../util';


describe('the ANOVA page', () => {
  it('analyze table and select metabolite', async () => {
    let selectedMetabolites;
    await expect(page).toClickXPath(vBtn('Your Datasets'));

    await uploadDataset('anovaTest');
    await expect(page).toClickXPath(vListTile({ title: 'anovaTest.csv ', content: 'Dataset ready for analysis.' }) + vBtn('View Data'));

    // click analyze table
    await expect(page).toClickXPath(vListTile({ title: 'Analyze Table' }));

    // click ANOVA
    await expect(page).toClickXPath(vListTile({ title: 'ANOVA' }));

    // select some metabolites from ANOVA by adding the highlighted Metabolites to the selected set
    /* eslint prefer-template: "off" */
    await expect(page).toClickXPath("//*[text()='C26 - C26.Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // the 'Alanine' row has been selected
    await expect(selectedMetabolites).toHaveLength(1);

    await expect(page).toClickXPath("//*[text()='C26 - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // 'Glutamine', 'Nicotinurate', 'Sarcosine' rows have been selected
    await expect(selectedMetabolites).toHaveLength(4);

    await expect(page).toClickXPath("//*[text()='C26 - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // 'Aspartate', 'Glucose', 'Glutathione' rows have been selected
    await expect(selectedMetabolites).toHaveLength(7);

    await expect(page).toClickXPath("//*[text()='C26.Fol - Fol']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // the 'Taurine' has been selected
    await expect(selectedMetabolites).toHaveLength(8);

    await expect(page).toClickXPath("//*[text()='C26.Fol - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // 'Glutamate', 'Leucine', 'Phenylalanine' rows have been selected
    await expect(selectedMetabolites).toHaveLength(11);

    await expect(page).toClickXPath("//*[text()='Fol - Veh']" + vBtn({ title: 'Adds the highlighted Metabolites to the selected set' }));
    selectedMetabolites = await page.$x("//div[@class='v-input v-input--selection-controls v-input--checkbox v-input--hide-details v-input--is-label-active v-input--is-dirty theme--light']");
    // the 'Malate' row has been selected
    await expect(selectedMetabolites).toHaveLength(12);
  });
});
