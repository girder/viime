<script>
export default {
  data() {
    return {
      visible: false,
      src: 'https://docs.google.com/forms/d/e/1FAIpQLScWccZqTF_b6nQkfkAvLNf7XGV9k7Rqf8V_Mid-oZLY47g_IQ/viewform?embedded=true',
    };
  },
};
</script>

<template lang="pug">
v-dialog(v-model="visible", width="640", lazy)
  template(#activator="{ on }")
    v-btn(v-on="on", icon, title="submit feedback")
      v-icon {{ $vuetify.icons.feedback }}

  iframe.iframe(:src="src",
      width="640", height="891", frameborder="0", marginheight="0", marginwidth="0")
</template>
<style lang="scss" scoped>
.iframe {
  background: white;
}
</style>
