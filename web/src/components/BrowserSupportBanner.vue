<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { getBrowser } from '../utils';

@Component
export default class BrowserSupportBanner extends Vue {
  // eslint-disable-next-line class-methods-use-this
  get showBanner() {
    const browser = getBrowser();
    return !(browser.isBlink || browser.isFirefox);
  }
}
</script>

<template lang="pug">
v-toolbar(dense, color="warning", v-if="showBanner")
  v-icon $vuetify.icons.warningCircle
  v-toolbar-title Browser Unsupported
  .subheading.px-4 Certain features require Chrome or Firefox
</template>
