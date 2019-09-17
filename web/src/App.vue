<template lang="pug">
v-app
  v-toolbar.darken-3(dense, dark, color="primary")
    v-toolbar-side-icon.logo(@click="$router.push('/')") BA
    v-breadcrumbs(:items="breadcrumbs", divider="»")
      template(#item="props")
        v-breadcrumbs-item(:to="props.item.to") {{props.item.text}}
    v-spacer
    //- v-btn(icon)
    //-   v-icon {{ $vuetify.icons.settings }}
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
          text: 'Biomarker Analysis',
          to: '/',
          disabled: false,
        },
        {
          text: this.$route.name,
          to: this.$route.path,
          disabled: false,
        },
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
