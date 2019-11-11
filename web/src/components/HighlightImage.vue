<script>
export default {
  props: {
    small: {
      type: Boolean,
      required: false,
    },
  },
};

</script>

<template lang="pug">
.highlight-image
  img.inner(alt="VIIME", v-if="small",
      src="../assets/banner_0_5k.jpg",
      srcset="../assets/banner_0_5k.jpg 0.5x,\
            ../assets/banner_1k.jpg 1x,\
            ../assets/banner_2k.jpg 2x")
  img.inner(alt="VIIME", v-else,
      src="../assets/banner_1k.jpg",
      srcset="../assets/banner_0_5k.jpg 0.5x,\
            ../assets/banner_1k.jpg 1x,\
            ../assets/banner_2k.jpg 2x")
</template>

<style scoped lang="scss">

.highlight-image {
  position: relative;
  filter: drop-shadow(2px 2px 3px black);
}

.inner {
  mask-image: url('../assets/viime_mask.svg');
  mask-repeat: no-repeat;
  mask-size: contain;
  mask-position: center center;

  position: relative;
  height: auto;
  width: 100%;
}

@media screen and (max-width: 960px) {
  .highlight-image {
    max-height: 275px;
    margin: 0 auto;
    width: auto;
  }
  .inner {
    max-height: 275px;
  }
}
</style>
