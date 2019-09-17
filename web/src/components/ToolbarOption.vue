<script>
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
    value: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
};
</script>

<template lang="pug">
div
  v-toolbar.darken-3(color="primary", dark, flat, dense, :card="false")
    v-toolbar-title {{title}}
  v-card.mx-3(flat)
    v-card-actions
      v-radio-group.my-0(:value="value",
          hide-details,
          @change="$emit('change', $event)")
        v-radio(v-for="m in options", :label="m.label",
            :value="m.value", :key="m.value")
</template>
