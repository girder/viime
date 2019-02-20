<template lang="pug">
v-app
  v-toolbar(dark)
    v-toolbar-title
      img(src="./assets/logo.png", width="48px", height="48px")
    v-spacer
    v-toolbar-title
      b Biomarker Analysis
    v-spacer
    v-btn(icon)
      v-icon more_vert
  v-toolbar(dense, dark, color="primary")
    v-spacer
    b 1.0 {{ $router.currentRoute.name }}
    v-spacer
  v-layout(column)
    router-view.grow
</template>

<script>
import Upload from './components/Upload.vue';

export default {
  name: 'app',
  components: {
    Upload,
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
