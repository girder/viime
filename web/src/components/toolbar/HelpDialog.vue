<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

@Component
export default class HelpDialog extends Vue {
  @Prop({
    default: '',
  })
  readonly title!: string;

  @Prop({
    default: '',
  })
  readonly text!: string;

  @Prop({
    default: false,
  })
  readonly outline!: boolean;

  showHelp = false;
}
</script>

<template lang="pug">
v-dialog(v-model="showHelp", max-width="33vw")
  template(v-slot:activator="{ on }")
    v-btn.ma-0(v-on="on", icon, small, depressed, flat)
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
