import { CLIENT_URL } from '../util';
import { vBtn } from 'jest-puppeteer-vuetify';

  describe('home page ', () => {
    it('load home page', async () => {
      await Promise.all([
        page.goto(CLIENT_URL),
        page.waitForNavigation({ waitUntil: 'networkidle0' }),
      ]);
    });

    it('click button', async () => {
      await expect(page).toClickXPath(vBtn('Your Datasets'));
    });
  });
