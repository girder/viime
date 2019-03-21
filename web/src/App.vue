<template lang="pug">
v-app
  v-toolbar.darken-3(dark, flat, color="secondary")
    v-toolbar-title
      img(src="./assets/logo.png", width="48px", height="48px")
    v-spacer
    v-toolbar-title
      b Biomarker Analysis > {{ $router.currentRoute.name }}
    v-spacer
    v-btn(icon)
      v-icon {{ $vuetify.icons.more }}
  v-container.pa-0.d-flex(fluid, column)
    router-view.grow
</template>

<script>

export default {
  name: 'App',
};
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  max-height: 100vh;
}
</style>
