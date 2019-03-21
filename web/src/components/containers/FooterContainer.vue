<script>
export default {
  name: 'FooterContainer',
};
</script>

<template lang="pug">
v-layout.footer-container(column, fill-height)
  .content-area
    slot
  slot(name="footer")
</template>

<style lang="scss">
.footer-container {
  .content-area {
    overflow: auto;
    height: 100%;
  }

  .v-toolbar.footer {
    border-top: 3px solid #cdd0d1;
  }
}
</style>
