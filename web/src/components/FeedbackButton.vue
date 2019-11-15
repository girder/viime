<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

@Component
export default class FeedbackButton extends Vue {
  @Prop({
    default: false,
  })
  readonly front!: boolean;

  visible = false;

  form = 'https://docs.google.com/forms/d/e/1FAIpQLScWccZqTF_b6nQkfkAvLNf7XGV9k7Rqf8V_Mid-oZLY47g_IQ/viewform';

  width = 640;

  height = 930;

  get src() {
    return `${this.form}?embedded=true`;
  }
}
</script>

<template lang="pug">
v-btn(v-if="front", :href="form", depressed, large,
    target="_blank", rel="noopener noreferrer")
  v-icon.mr-2(left) {{ $vuetify.icons.feedback }}
  | Contact us

v-dialog(v-else, v-model="visible", :width="width", lazy)
  template(#activator="{ on }")
    v-btn(v-on="on", icon, title="submit feedback")
      v-icon {{ $vuetify.icons.feedback }}

  iframe.iframe(:src="src", :width="width", :height="height",
      frameborder="0", marginheight="0", marginwidth="0")
</template>
<style lang="scss" scoped>
.iframe {
  background: white;
}
</style>
