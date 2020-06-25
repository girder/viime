<script>
export default {
  props: {
    title: {
      type: String,
      default: '',
    },
    text: {
      type: String,
      default: '',
    },
    outline: {
      type: Boolean,
      default: false,
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
    v-btn.ml-auto.mr-0(v-on="on", icon, small, depressed, flat)
      v-icon(:color="outline ? 'rgba(0,0,0,0.25)' : undefined", small)
        | {{ outline ? $vuetify.icons.helpOutline : $vuetify.icons.help }}
  v-card
    v-card-title
      h3.headline {{ title }}
    v-card-text
      slot
        | {{ text }}
    v-card-actions
      v-spacer
      v-btn(@click="showHelp = false") Close
</template>
