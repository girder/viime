import { vBtn } from 'jest-puppeteer-vuetify';
import { CLIENT_URL } from '../util';


describe('home page', () => {
  // eslint-disable-next-line jest/expect-expect
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
