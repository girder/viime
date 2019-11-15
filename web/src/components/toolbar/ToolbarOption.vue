<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import HelpDialog from './HelpDialog.vue';

@Component({
  components: {
    HelpDialog,
  },
})
export default class ToolbarOption extends Vue {
  @Prop({
    default: '',
  })
  readonly title!: string;

  @Prop({
    required: true,
  })
  readonly value!: string;

  @Prop({
    default: false,
  })
  readonly disabled!: boolean;

  @Prop({
    required: true,
  })
  readonly options!: {label: string, value: string, helpText?: string}[];
}
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
            span.grow {{ m.label }}
            help-dialog(v-if="m.helpText", :title="`${m.label} ${title}`",
                :text="m.helpText", outline)
</template>

<style scoped>
.wide >>> .v-label {
  flex: 1 1 0;
}
</style>
