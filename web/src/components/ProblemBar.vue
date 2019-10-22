<script>
import { CHANGE_AXIS_LABEL } from '@/store/actions.type';
import { SET_SELECTION } from '@/store/mutations.type';
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
  methods: {
    base26Converter,
    select(event, item) {
      const { index } = item;
      this.$store.commit(SET_SELECTION, {
        key: this.id,
        idx: index,
        axis: 'column',
        event,
      });
    },
    async mask(index) {
      const changes = [{
        context: this.problemData.context,
        index,
        label: 'masked',
      }];
      await this.$store.dispatch(CHANGE_AXIS_LABEL, { dataset_id: this.id, changes });
    },
    async maskAll() {
      const { problemData } = this;
      const changes = problemData.data.map(error => ({
        context: problemData.context,
        index: error.index,
        label: 'masked',
      }));
      await this.$store.dispatch(CHANGE_AXIS_LABEL, { dataset_id: this.id, changes });
    },
  },
};
</script>

<template lang="pug">
v-navigation-drawer.primary.darken-3.problem-bar-component(v-if="dataset && problemData",
    touchless, permanent, floating, style="width: 230px; min-width: 220px;")

  v-layout(column, fill-height)
    v-btn(large, color="error", @click="maskAll") Mask all

    v-toolbar.primary.darken-3(dark, flat, dense, :card="false")
      v-toolbar-title
        .headline {{ problemData.title }}

    v-container.grow-overflow.ma-0.pa-0.mainContainer(grid-list-lg)
      v-card.mx-2.my-1(flat,
          v-for="item in problemData.data",
          :key="base26Converter(item.index + 1)")
        v-card-title.pa-2
          div
            .title(
                style="text-decoration:underline; cursor: pointer;",
                @click="select($event, item)")
              | {{ base26Converter(item.index + 1) }}:
              | {{ item.name }}
            .body-1 {{ item.info }}
        v-card-actions.pt-0.pb-1
          v-spacer
          v-btn.ma-0(icon, small, flat, color="error", @click="mask(item.index)")
            v-icon {{ $vuetify.icons.masked }}
</template>
