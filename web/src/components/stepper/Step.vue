<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    small: {
      type: Boolean,
      default: true,
    },
    state: {
      type: Number,
      required: true,
    },
  },
  computed: {
    done() {
      return this.state > 0;
    },
    inprogress() {
      return this.state === 0;
    },
    pending() {
      return this.state < 0;
    },
    classes() {
      const {
        done, inprogress, pending, small,
      } = this;
      return {
        icon: {
          // background colors
          collapsed: small,
          accent: done || inprogress,
          'lighten-4': done,
          secondary: done,
          // icon colors
          'white--text': inprogress,
          'accent--text': done,
        },
        text: {
          'primary--text': done || pending,
          'text--darken-3': done || pending,
          'accent--text': inprogress,
        },
      };
    },
  },
};
</script>

<template lang="pug">
.step
  v-layout.px-3(column, align-center)
    .outer-wrap.shrink
      .icon-wrapper.secondary.lighten-5
        v-icon.icon(
            :large="!small",
            :small="small",
            :class="classes.icon") {{ this.done ? $vuetify.icons.check : $vuetify.icons[icon] }}
    h4.title.font-weight-bold.pa-1(v-if="!small", :class="classes.text") {{ name }}
    p.narrow.caption.secondary--text.text--lighten-2(v-if="!small") {{ description }}
</template>

<style lang="scss" scoped>
.step {
  z-index: 4;

  .icon-wrapper {
    padding: 3px;
    border-radius: 50%;

    .icon {
      padding: 8px;
      border-radius: 50%;
      vertical-align: baseline;

      &.collapsed {
        padding: 5px;
      }
    }
  }

  .narrow {
    max-width: 120px;
    text-align: center;
    line-height: 1;
  }
}
</style>
