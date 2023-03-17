<script lang="ts">
import { defineComponent, computed } from '@vue/composition-api';

export default defineComponent({
  setup() {
    // Adapted from https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
    const showBanner = computed(() => {
      // Opera 8.0+
      // @ts-ignore
      // eslint-disable-next-line no-undef
      const isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

      // Chrome 1 - 71
      // @ts-ignore
      const isChrome = !!window.chrome;

      // Blink engine detection
      const isBlink = (isChrome || isOpera) && !!window.CSS;

      // Firefox 1.0+
      // @ts-ignore
      const isFirefox = typeof InstallTrigger !== 'undefined';

      return !(isBlink || isFirefox);
    });
    return { showBanner };
  },
});
</script>

<template>
  <v-toolbar
    v-if="showBanner"
    dense
    color="warning"
  >
    <v-icon> $vuetify.icons.warningCircle </v-icon>
    <v-toolbar-title> Browser Unsupported </v-toolbar-title>
    <div class="subheading px-4">
      Certain features require Chrome or Firefox
    </div>
  </v-toolbar>
</template>
