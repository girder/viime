<template lang="pug">
v-toolbar(dense, color="warning", v-if="showBanner")
  v-icon $vuetify.icons.warningCircle
  v-toolbar-title Browser Unsupported
  .subheading.px-4 Certain features require Chrome or Firefox
</template>

<script>
import { getBrowser } from '../utils/mixins';

export default {
  mixins: [getBrowser],
  computed: {
    showBanner() {
      return !(this.browser.isBlink || this.browser.isFirefox);
    },
  },
};
</script>
