<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api';

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    text: {
      type: String,
      required: false,
      default: '',
    },
    outline: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  setup() {
    const showHelp = ref(false);
    return { showHelp };
  },
});
</script>

<template>
  <v-dialog
    v-model="showHelp"
    max-width="33vw"
  >
    <template v-slot:activator="{ on }">
      <v-btn
        class="ml-auto mr-0"
        icon="icon"
        small="small"
        depressed="depressed"
        flat="flat"
        v-on="on"
      >
        <v-icon
          :color="outline ? 'rgba(0,0,0,0.25)' : undefined"
          small="small"
        >
          {{ outline ? $vuetify.icons.helpOutline : $vuetify.icons.help }}
        </v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <h3 class="headline">
          {{ title }}
        </h3>
      </v-card-title>
      <v-card-text>
        <slot>{{ text }}</slot>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="showHelp = false">
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
