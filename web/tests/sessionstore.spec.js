import SessionStore from '../src/utils/sessionStore';

describe('SessionStore', () => {
  it('Loads correct defaults from localStorage', () => {
    const mockProvider = {
      localStorage: {
        getItem: () => '',
      },
    };
    const ss = new SessionStore(mockProvider);
    const defaults = ss.load('does_not_matter');
    expect(Object.keys(defaults.datasets).length).toBe(0);
  });

  it('Sets the correct defaults when localStorage becomes corrupt', () => {
    let storageVal = null;
    const mockProvider = {
      localStorage: {
        getItem: () => '{ invalid json',
        setItem: (key, newval) => storageVal = newval,
      },
    };
    const ss = new SessionStore(mockProvider);
    ss.load('sessionstring');
    expect(JSON.parse(storageVal)).toHaveProperty('sessionstring');
  });
});
