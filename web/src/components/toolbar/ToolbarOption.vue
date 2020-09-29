<script lang="ts">
import { PropType, defineComponent } from '@vue/composition-api';
import HelpDialog from './HelpDialog.vue';

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    value: {
      type: String,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
    options: {
      type: Array as PropType<Array<{
        label: string; value: string;
        helpText?: string;
      }>>,
      required: true,
    },
  },
  components: {
    HelpDialog,
  },
});
</script>

<template>
  <div>
    <v-toolbar
      class="darken-3"
      color="primary"
      dark
      flat
      dense
      :card="false"
    >
      <v-toolbar-title>
        <slot>{{ title }}</slot>
      </v-toolbar-title>
    </v-toolbar>
    <v-card
      class="mx-3"
      flat
    >
      <v-card-actions>
        <v-radio-group
          class="my-0"
          :value="value"
          hide-details
          :disabled="disabled"
          @change="$emit('change', $event)"
        >
          <v-radio
            v-for="m in options"
            :key="m.value"
            class="wide mr-0"
            :value="m.value"
          >
            <template #label>
              <span
                class="grow groupCombinationContainer"
                :title="m.label"
              >{{ m.label }}</span>
              <help-dialog
                v-if="m.helpText"
                :title="`${m.label} ${title}`"
                :text="m.helpText"
                outline
              />
            </template>
          </v-radio>
        </v-radio-group>
      </v-card-actions>
    </v-card>
  </div>
</template>

<style scoped>
.groupCombinationContainer {
  position: absolute;
  width: 100px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.wide >>> .v-label {
  flex: 1 1 0;
}
</style>

<style>
/* This fixes a bug that was fixed in Vuetify 2.1 */
/* See https://github.com/vuetifyjs/vuetify/issues/5416#issuecomment-567106519 */
/* TODO Remove this once the version is bumped */
.v-input--selection-controls .v-input__control {
  width: 100% !important;
}
</style>
