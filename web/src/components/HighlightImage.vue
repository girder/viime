<script>
export default {
  props: {
    small: {
      type: Boolean,
      required: false,
    },
  },
  computed: {
    src() {
      if (this.small) {
        return 'https://placekitten.com/1000/1040';
      }
      return 'https://placekitten.com/2000/2081';
    },
  },
};

</script>

<template lang="pug">
.highlight-image
  img.inner(alt="VIIME", :src="src")
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
