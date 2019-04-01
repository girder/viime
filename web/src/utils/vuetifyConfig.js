/**
 * This is the Vuetify configuration Object needed to use Girder components. This is provided so
 * that downstreams who are using Vuetify can merge their own Vuetify config options prior to
 * installing the GirderVue plugin.
 */

import colors from 'vuetify/es5/util/colors';

export default {
  theme: {
    primary: colors.blueGrey,
    secondary: colors.grey,
    accent: colors.lightGreen,
    error: colors.red,
    info: colors.lightBlue.lighten1,
    warning: colors.yellow.darken2,
  },
  icons: {
    alert: 'mdi-alert',
    arrowLeft: 'mdi-arrow-left-box',
    arrowRight: 'mdi-arrow-right-box',
    bubbles: 'mdi-chart-bubble',
    check: 'mdi-check',
    checkedFlag: 'mdi-flag-checkered',
    chevronDown: 'mdi-chevron-down',
    chevronUp: 'mdi-chevron-up',
    clearAll: 'mdi-notification-clear-all',
    error: 'mdi-close',
    eyedropper: 'mdi-eyedropper',
    group: 'mdi-group',
    header: 'mdi-key-variant',
    info: 'mdi-information',
    masked: 'mdi-eye-off',
    more: 'mdi-dots-horizontal',
    menuDown: 'mdi-menu-down',
    metadata: 'mdi-tag',
    key: 'mdi-key-variant',
    save: 'mdi-content-save',
    tableEdit: 'mdi-table-edit',
    transform: 'mdi-set-right',
    upload: 'mdi-upload',
    warning: 'mdi-alert',
  },
};
