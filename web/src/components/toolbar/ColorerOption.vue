<script lang="ts">
import { defineComponent, PropType, computed } from '@vue/composition-api';

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    value: {
      type: String,
      required: false,
      default: null,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
    options: {
      type: Array as PropType<Array<{
        name: string;
        value: string;
        options: Array<{
          name: string;
          color?: string;
        }>;
      }>>,
      required: true,
    },
  },
  setup(props) {
    const showSelect = computed(() => !props.value || props.options.length > 1);
    const filterOptions = computed(() => {
      const selected = props.options.find((d) => d.value === props.value);
      return selected ? selected.options : [];
    });
    const hasOptions = computed(() => {
      if (props.options.length === 0) {
        return false;
      }
      if (props.options.length === 1 && !props.options[0].value) {
        return false;
      }
      return true;
    });
    return {
      showSelect,
      filterOptions,
      hasOptions,
    };
  },
});
</script>

<template>
  <div v-if="hasOptions">
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
      <v-card-actions style="display: block">
        <v-select
          v-if="showSelect"
          class="my-0"
          :value="value"
          hide-details
          :disabled="disabled"
          :items="options"
          item-text="name"
          @change="$emit('input', $event)"
        />
        <div
          v-for="o in filterOptions"
          :key="o.name"
          class="my-0 option"
          :title="o.name"
        >
          <v-icon :color="o.color">
            {{ $vuetify.icons.square }}
          </v-icon>{{ o.name }}
        </div>
      </v-card-actions>
    </v-card>
  </div>
</template>

<style scoped>
.option {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
