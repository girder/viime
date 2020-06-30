// import { CLIENT_URL } from '../util';

import { vBtn } from 'jest-puppeteer-vuetify';
import { toClickXPath } from 'jest-puppeteer-vuetify/src/jest-xpaths';

  describe('home page ', () => {
    it('load home page', async () => {
      await Promise.all([
        //
        //  page.goto(CLIENT_URL),
        page.goto('http://localhost:8080'),
        page.waitForNavigation({ waitUntil: 'networkidle0' }),
      ]);
    });

    // propably need to use the jest-puppeteer-vuetify helper
    it('click button', async () => {
      // await expect(page).toClick('button', { text: 'Your Datasets' });
      // toClickXPath
      await expect(page).toClickXPath(vBtn('Your Datasets'));
    });
  });


  // await Promise.all([
  //   expect(page).toClickXPath(vBtn('Your Datasets')),
  //   page.waitForNavigation({ waitUntil: 'networkidle0' }),
  // ]);
