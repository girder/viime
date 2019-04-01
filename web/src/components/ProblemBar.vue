<script>
import { base26Converter } from '@/utils/';

export default {
  props: {
    id: {
      type: String,
      required: true,
    },
    problem: {
      type: String,
      required: true,
    },
  },
  computed: {
    dataset() {
      return this.$store.state.datasets[this.id];
    },
    problemData() {
      return this.dataset.validation.find(v => v.type === this.problem);
    },
  },
  methods: { base26Converter },
};
</script>

<template lang="pug">
v-navigation-drawer.primary.darken-3(v-if="dataset",
    touchless, floating, style="width: 200px; min-width: 200px;")

  v-layout(column, fill-height)

    v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
      v-toolbar-title
        .headline {{ problemData.title }}

    v-card.mx-2.my-1(flat, v-for="item in problemData.data")
      v-card-title.pa-2
        div
          .title(
              style="text-decoration:underline; cursor: pointer;",
              @click="$emit('select', item.index)") Column {{ base26Converter(item.index) }}
          .body-1 {{ item.info }}
        v-spacer
        v-btn.ma-0(icon, small, flat, color="error")
          v-icon {{ $vuetify.icons.masked }}
    v-btn(large, color="error") Mask all
</template>
