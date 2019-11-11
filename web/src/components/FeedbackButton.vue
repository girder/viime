<script>
export default {
  props: {
    front: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      visible: false,
      src: 'https://docs.google.com/forms/d/e/1FAIpQLScWccZqTF_b6nQkfkAvLNf7XGV9k7Rqf8V_Mid-oZLY47g_IQ/viewform?embedded=true',
      width: 640,
      height: 930,
    };
  },
};
</script>

<template lang="pug">
v-dialog(v-model="visible", :width="width", lazy)
  template(#activator="{ on }")
    v-btn.mt-3.mx-0.px-3(v-on="on", v-if="front", depressed, large)
      v-icon.mr-2(left) {{ $vuetify.icons.feedback }}
      | Contact us
    v-btn(v-on="on", icon, title="submit feedback", v-else)
      v-icon {{ $vuetify.icons.feedback }}

  iframe.iframe(:src="src", :width="width", :height="height",
      frameborder="0", marginheight="0", marginwidth="0")
</template>
<style lang="scss" scoped>
.iframe {
  background: white;
}
</style>
