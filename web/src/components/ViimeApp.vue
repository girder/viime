<template lang="pug">
v-app.viime-app
  v-toolbar.darken-3(dense, dark, color="primary")
    v-toolbar-side-icon.logo(:to="{name: 'Root'}") V
    v-breadcrumbs(:items="breadcrumbs", divider="»")
      template(#item="props")
        v-breadcrumbs-item(:to="props.item.to", exact) {{props.item.text}}

    v-spacer

    save-status

  v-container.pa-0.d-flex(fluid)
    router-view.grow
</template>

<script>
import SaveStatus from './SaveStatus.vue';

export default {
  name: 'App',
  components: {
    SaveStatus,
  },
  computed: {
    breadcrumbs() {
      return [
        {
          text: 'VIIME',
          to: { name: 'Upload Data' },
        },
        ...this.$route.matched.filter(route => !route.meta.hidden).map((route) => {
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

  .logo.v-btn--icon {
    font-size: 150%;
    color: transparent;
    background: url("../assets/favicon.svg") no-repeat center center;
    background-size: 80%;
    border-radius: unset;
  }

  .v-breadcrumbs li {
    font-size: 20px;

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
