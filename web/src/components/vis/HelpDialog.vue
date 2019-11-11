<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      showHelp: false,
    };
  },
};
</script>

<template lang="pug">
v-dialog(v-model="showHelp", max-width="33vw")
  template(v-slot:activator="{ on }")
    v-btn(v-on="on", icon)
      v-icon {{ $vuetify.icons.help }}
  v-card
    v-card-title
      h3.headline {{ title }}
    v-card-text
      slot
    v-card-actions
      v-spacer
      v-btn(@click="showHelp = false") Close
</template>
