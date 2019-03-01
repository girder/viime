/**
 * This is the Vuetify configuration Object needed to use Girder components. This is provided so
 * that downstreams who are using Vuetify can merge their own Vuetify config options prior to
 * installing the GirderVue plugin.
 */

import colors from 'vuetify/es5/util/colors';

export default {
  theme: {
    primary: colors.lightGreen.lighten1,
    secondary: colors.blueGrey,
    accent: colors.lightGreen,
    error: colors.red,
    info: colors.lightBlue.lighten1,
  },
  icons: {
    more: 'mdi-dots-horizontal',
    menuDown: 'mdi-menu-down',
    arrowRight: 'mdi-arrow-right-box',
  },
};
