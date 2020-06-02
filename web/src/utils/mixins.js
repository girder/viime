import { LOAD_DATASET } from '../store/actions.type';
import { INTIALIZE_DATASET } from '../store/mutations.type';

/**
 * Load dataset from server for any view where
 * dataset_id is defined
 */
const loadDataset = {
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  computed: {
    datasetLoaded() {
      return !!this.$store.state.datasets[this.id];
    },
  },
  created() {
    const dataset = this.$store.getters.dataset(this.id);
    if (!dataset) {
      // initialize the dataset to prevent NPE race conditions during slow loads
      this.$store.commit(INTIALIZE_DATASET, { dataset_id: this.id });
      this.$store.dispatch(LOAD_DATASET, { dataset_id: this.id });
    }
  },
};

// Adapted from https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
const getBrowser = {
  computed: {
    browser() {
      // Opera 8.0+
      // eslint-disable-next-line no-undef
      const isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

      // Firefox 1.0+
      const isFirefox = typeof InstallTrigger !== 'undefined';

      // Safari 3.0+ "[object HTMLElementConstructor]"
      // eslint-disable-next-line wrap-iife,func-names,quotes,dot-notation,no-undef
      const isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || (typeof safari !== 'undefined' && safari.pushNotification));

      // Internet Explorer 6-11
      // eslint-disable-next-line spaced-comment
      const isIE = /*@cc_on!@*/false || !!document.documentMode;

      // Edge 20+
      const isEdge = !isIE && !!window.StyleMedia;

      // Chrome 1 - 71
      const isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);

      // Blink engine detection
      const isBlink = (isChrome || isOpera) && !!window.CSS;

      return {
        isOpera,
        isFirefox,
        isSafari,
        isIE,
        isEdge,
        isChrome,
        isBlink,
      };
    },
  },
};

export {
  getBrowser,
  loadDataset,
};
