
<template lang="pug">
v-app
  router-view
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
}
</style>
