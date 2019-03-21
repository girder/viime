<template lang="pug">
v-layout(column, fill-height)
  .content-area
    slot
  slot(name='footer')
</template>

<script>
export default {
  name: 'FooterContainer',
};
</script>

<style>
.content-area {
  overflow: auto;
  height: 100%;
}
</style>
