<template lang="pug">
v-app
  v-toolbar.main-toolbar.darken-3(dark, dense, flat, color="primary")
    v-toolbar-items
      v-btn.px-0.square-button.darken-4(flat, color="white")
        v-icon {{ $vuetify.icons.close }}
    v-spacer
    v-toolbar-title.title
      span.font-weight-bold.secondary--text.text--lighten-2 Biomarker Analysis »
      span.font-weight-bold.white--text  {{ $router.currentRoute.name }}
    v-spacer
    v-btn(icon)
      v-icon {{ $vuetify.icons.more }}
  v-container.pa-0.d-flex(fluid)
    router-view.grow
</template>

<script>

export default {
  name: 'App',
};
</script>

<style lang="scss">
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  max-height: 100vh;
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
  }
}
</style>
