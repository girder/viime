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
  },
  icons: {
    arrowLeft: 'mdi-arrow-left-box',
    arrowRight: 'mdi-arrow-right-box',
    check: 'mdi-check',
    checkedFlag: 'mdi-flag-checkered',
    chevronDown: 'mdi-chevron-down',
    chevronUp: 'mdi-chevron-up',
    clearAll: 'mdi-notification-clear-all',
    eyedropper: 'mdi-eyedropper',
    more: 'mdi-dots-horizontal',
    menuDown: 'mdi-menu-down',
    key: 'mdi-key-variant',
    save: 'mdi-content-save',
    tableEdit: 'mdi-table-edit',
    tag: 'mdi-tag',
    transform: 'mdi-set-right',
    upload: 'mdi-upload',
  },
};
