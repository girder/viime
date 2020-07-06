import { vBtn } from 'jest-puppeteer-vuetify';
import { CLIENT_URL } from '../util';

describe('home page', () => {
  it('load home page', async () => {
    await Promise.all([
      expect(page).goto(CLIENT_URL),
      expect(page).waitForNavigation({ waitUntil: 'networkidle0' }),
    ]);
  });

  it('click button', async () => {
    await expect(page).toClickXPath(vBtn('Your Datasets'));
  });
});
