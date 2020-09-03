<script lang="ts">
import { PropType, defineComponent, computed } from '@vue/composition-api';

export default defineComponent({
  props: {
    title: {
      type: String,
      required: false,
      default: '',
    },
    value: {
      type: Object as PropType<{
        option: string | null;
        filter: string[];
      }>,
      required: true,
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
          color?: string;
          value: string;
        }>;
      }>>,
      required: true,
    },
  },
  setup(props, { emit }) {
    const showSelect = computed(() => !props.value || props.options.length > 1);
    const selected = computed({
      get() {
        return props.value?.option;
      },
      set(value: string | null) {
        if (!value) {
          emit('input', { option: null, filter: [] });
        } else {
          const selectedOption = props.options.find((d) => d.value === value);
          if (selectedOption) {
            emit('input', { option: value, filter: selectedOption.options.map((d) => d.value) });
          }
        }
      },
    });
    const filterOptions = computed(() => {
      const selectedOption = props.options.find((d) => d.value === selected.value);
      return selectedOption ? selectedOption.options : [];
    });
    const filter = computed({
      get() {
        return props.value ? props.value.filter : [];
      },
      set(values) {
        emit('input', { ...props.value, filter: values });
      },
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
      selected,
      filterOptions,
      filter,
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
      dark="dark"
      flat="flat"
      dense="dense"
      :card="false"
    >
      <v-toolbar-title>
        <slot>{{ title }}</slot>
      </v-toolbar-title>
    </v-toolbar>
    <v-card
      class="mx-3"
      flat="flat"
    >
      <v-card-actions style="display: block">
        <v-select
          v-if="showSelect"
          v-model="selected"
          class="my-0"
          hide-details="hide-details"
          :disabled="disabled"
          :items="options"
          item-text="name"
        />
        <v-checkbox
          v-for="o in filterOptions"
          :key="o.name"
          v-model="filter"
          class="my-0 option"
          :label="o.name"
          :value="o.value"
          :title="o.name"
          hide-details="hide-details"
          :color="o.color"
        />
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
