class SessionStore {
  /**
   * @param {WindowLocalStorage} provider localStorageApi provider
   */
  private provider: WindowLocalStorage;


  constructor(provider: WindowLocalStorage) {
    this.provider = provider;
  }

  load(sessionId = 'default') {
    const sessionString = this.provider.localStorage.getItem('session') || '{}';
    try {
      const session = JSON.parse(sessionString);
      const { datasets = {} } = session[sessionId] || {};
      return { datasets };
    } catch (err) {
      this.provider.localStorage.setItem(
        'session',
        JSON.stringify({ [sessionId]: { datasets: {} } }),
      );
      return { datasets: {} };
    }
  }

  save(state: any, sessionId = 'default') {
    const rawDatasetIDs = Object.keys(state.datasets);
    const datasets: {[key: string]: any} = {};
    rawDatasetIDs.forEach((id) => {
      // the keys from dataset to cache in localStorage;
      const d = state.datasets[id];
      const {
        name,
        size,
        width,
        height,
        validation,
        selected,
      } = d;
      datasets[id] = {
        id,
        name,
        size,
        width,
        height,
        validation,
        selected,
        ready: false,
      };
    });
    this.provider.localStorage.setItem('session', JSON.stringify({
      [sessionId]: { datasets },
    }));
  }
}

export default SessionStore;
