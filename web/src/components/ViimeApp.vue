<template lang="pug">
v-app
  v-toolbar.darken-3(dense, dark, color="primary")
    v-toolbar-side-icon.logo(@click="$router.push('/')") V
    v-breadcrumbs(:items="breadcrumbs", divider="»")
      template(#item="props")
        v-breadcrumbs-item(:to="props.item.to", exact) {{props.item.text}}
  v-container.pa-0.d-flex(fluid)
    router-view.grow
</template>

<script>

export default {
  name: 'App',
  computed: {
    breadcrumbs() {
      return [
        {
          text: 'VIIME',
          to: { name: 'Root' },
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
  .logo.v-btn--icon {
    font-size: 150%;
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
