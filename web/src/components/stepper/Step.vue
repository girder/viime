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
    classes() {
      return {
        collapsed: this.small,
        pending: this.state < 0,
        inprogress: this.state === 0,
        done: this.state > 0,
      };
    },
  },
};
</script>

<template lang="pug">
.step
  v-layout.px-3(column, align-center)
    .outer-wrap.shrink
      .icon-wrapper
        v-icon.icon(
            :large="!small",
            :small="small",
            :class="classes") {{ this.done ? $vuetify.icons.check : $vuetify.icons[icon] }}
    h4.title.pa-1(v-if="!small") {{ name }}
    p.narrow.caption(v-if="!small") {{ description }}
</template>

<style lang="scss" scoped>
.step {
  z-index: 4;

  .icon-wrapper {
    background-color: #ECEFF1;
    padding: 3px;
    border-radius: 50%;

    .icon {
      padding: 8px;
      border-radius: 50%;
      vertical-align: baseline;

      &.collapsed {
        padding: 5px;
      }

      &.pending {
        background-color: #ECEFF1;
        color: #455A64;
      }

      &.inprogress {
        background-color: #9CCC65;
        color: white;
      }

      &.done {
        background-color: #F1F8E9;
        color: #9CCC65;
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
