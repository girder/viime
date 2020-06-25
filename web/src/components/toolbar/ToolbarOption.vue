<script>
import HelpDialog from './HelpDialog.vue';

export default {
  components: {
    HelpDialog,
  },
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
    },
    options: { // {label: string, value: string, helpText?: string}
      type: Array,
      required: true,
    },
  },
};
</script>

<template lang="pug">
div
  v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
    v-toolbar-title
      slot(name=title) {{title}}

  v-card.mx-3(flat)
    v-card-actions
      v-radio-group.my-0(:value="value",
          hide-details, :disabled="disabled",
          @change="$emit('change', $event)")
        v-radio.wide.mr-0(v-for="m in options",
            :value="m.value", :key="m.value")
          template(#label)
            span.grow.groupCombinationContainer(v-bind:title="m.label")
              | {{ m.label }}
            help-dialog(
                v-if="m.helpText",
                :title="`${m.label} ${title}`",
                :text="m.helpText", outline)
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
