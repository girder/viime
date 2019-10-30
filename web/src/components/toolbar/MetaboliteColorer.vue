<script>
import ColorerOption from './ColorerOption.vue';
import metaboliteMixin from './mixins/metaboliteMixin';
import { colors } from '../../utils/constants';

export default {
  components: {
    ColorerOption,
  },
  mixins: [metaboliteMixin],
  props: {
    title: {
      type: String,
      required: false,
      default: 'Metabolite Color',
    },
    value: { // {option: string | null, apply(column: string) => string | null}
      type: Object,
      required: false,
      default: null,
    },
  },
  computed: {
    validatedValue() {
      if (this.value) {
        return this.value;
      }
      if (this.options.length === 0) {
        return null;
      }
      return this.options[0].name;
    },
  },
  methods: {
    generateColorer(value) {
      if (!value) {
        return () => null;
      }
      if (value === 'Selection') {
        const isSelected = this.selectionLookup;
        return column => (isSelected(column) ? colors.selected : colors.notSelected);
      }
      const meta = this.categoricalMetaData.find(d => d.name === value.option);
      const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
      const toIndex = this.columnToIndex;
      return column => lookup.get(meta.data[toIndex(column)]);
    },
    changeValue(value) {
      const wrapper = {
        option: value,
        apply: this.generateColorer(value),
      };
      this.$emit('input', wrapper);
    },
  },
};
</script>

<template lang="pug">
colorer-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
