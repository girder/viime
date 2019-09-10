<template lang="pug">
v-app
  v-toolbar.main-toolbar.darken-4(dark, dense, color="primary")
    v-toolbar-items
      v-btn.px-0.square-button.darken-4(flat, color="white", to="/select")
        v-icon {{ $vuetify.icons.close }}
    v-spacer
    v-toolbar-title.title
      span.font-weight-bold.secondary--text.text--lighten-3 Biomarker Analysis »
      span.font-weight-bold.white--text  {{ $router.currentRoute.name }}
    v-spacer
  v-container.pa-0.d-flex(fluid, fill-height)
    router-view.grow
</template>

<script>
export default {
  name: 'App',
};
</script>

<style lang="scss">
body {
  overflow-x: auto;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  max-height: 100vh;
  min-width: 900px;

  .main-toolbar {
    .v-toolbar__content {
      padding-left: 0px;

      .square-button {
        min-width: 64px;
      }
    }
  }

  .overflow-auto {
    overflow: auto;
    max-height: 100%;
  }
}
</style>
