<script>
export default {
  name: 'HeaderFooter',
};
</script>

<template lang="pug">
v-layout.header-footer-container(column, fill-height)
  slot(name="header")
  .content-area
    slot
  slot(name="footer")
</template>

<style lang="scss">
.header-footer-container {
  .content-area {
    overflow: auto;
    height: 100%;
  }

  .v-toolbar.footer {
    border-top: 3px solid #cdd0d1;
  }
}
</style>
