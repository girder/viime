<template lang="pug">
v-app.viime-app
  browser-support-banner
  v-toolbar.main-toolbar.darken-3(dense, dark, color="primary")
    v-breadcrumbs(:items="breadcrumbs", divider="»")
      template(#item="props")
        v-breadcrumbs-item(:to="props.item.to", exact) {{props.item.text}}

    v-spacer

    feedback-button
    save-status
  v-container.pa-0.d-flex(fluid)
    router-view.grow
</template>

<script>
import BrowserSupportBanner from './BrowserSupportBanner.vue';
import SaveStatus from './SaveStatus.vue';
import FeedbackButton from './FeedbackButton.vue';

export default {
  name: 'App',
  components: {
    BrowserSupportBanner,
    SaveStatus,
    FeedbackButton,
  },
  computed: {
    breadcrumbs() {
      return [
        {
          text: 'VIIME',
          to: { name: 'Root' },
        },
        {
          text: 'Data',
          to: { name: 'Upload Data' },
        },
        ...this.$route.matched.filter((route) => !route.meta.hidden).map((route) => {
          const b = route.meta.breadcrumb;
          return {
            text: route.name,
            to: { name: route.name, params: this.$route.params },
            ...(b ? b.call(route, this.$route.params, this.$store) : {}),
          };
        }),
      ];
    },
  },
};
</script>

<style lang="scss">
.viime-app {
  min-width: 900px;

  .main-toolbar > .v-toolbar__content {
    padding-left: 2px;
  }

  .v-breadcrumbs li {
    font-size: 20px;

    &:first-of-type {
      color: transparent;
      background: url("../assets/viime_logo_ko.svg") no-repeat center center;
      background-size: auto 22px;

      > * {
        width: 65px;
      }
    }

    > a {
      color: inherit
    }
  }

  .grow-overflow {
    flex: 1 1 0;
    overflow: auto;
    max-height: 100%;
  }
}
</style>
