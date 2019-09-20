<template lang="pug">
v-app
  v-toolbar.darken-3(dense, dark, color="primary")
    v-toolbar-side-icon.logo(@click="$router.push('/')") V
    v-breadcrumbs(:items="breadcrumbs", divider="»")
      template(#item="props")
        v-breadcrumbs-item(:to="props.item.to", exact) {{props.item.text}}
    v-spacer
    //- v-btn(icon)
    //-   v-icon {{ $vuetify.icons.settings }}
  v-container.pa-0.d-flex(fluid)
    router-view.grow
</template>

<script>

function injectParams(path, params) {
  let parsed = path;
  Object.entries(params).forEach(([k, v]) => {
    parsed = parsed.replace(`:${k}`, v);
  });
  return parsed;
}

export default {
  name: 'App',
  computed: {
    breadcrumbs() {
      const toBreadcrumb = (route) => {
        const b = route.meta.breadcrumb;
        return {
          text: route.name,
          to: injectParams(route.path, this.$route.params),
          ...(b ? b.call(route, this.$route.params, this.$store) : {}),
        };
      };

      return [
        {
          text: 'VIIME',
          to: '/',
        },
        ...this.$route.matched.filter(d => !d.meta.hidden).map(d => toBreadcrumb(d)),
      ];
    },
  },
};
</script>

<style lang="scss">
body {
  overflow-x: auto;
}

.logo.v-btn--icon {
  // background: url('./assets/logo.png');
  // background-size: contain;
  font-size: 150%;
}

.v-breadcrumbs li {
  font-size: 20px;

  > a {
    color: inherit
  }
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  max-height: 100vh;
  min-width: 900px;

  .grow-overflow {
    flex: 1 1 0;
    overflow: auto;
    max-height: 100%;
  }
}
</style>
