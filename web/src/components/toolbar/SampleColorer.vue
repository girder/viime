<script>
import ColorerOption from './ColorerOption.vue';
import sampleMixin from './mixins/sampleMixin';

export default {
  components: {
    ColorerOption,
  },
  mixins: [sampleMixin],
  props: {
    title: {
      type: String,
      required: false,
      default: 'Sample Color',
    },
    value: { // {option: string | null, apply(row: string) => string | null}
      type: Object,
      required: false,
      default: null,
    },
  },
  computed: {
    validatedValue() {
      if (this.value) {
        return this.value.option;
      }
      if (this.options.length === 0) {
        return null;
      }
      const v = this.options[0].name;
      this.changeValue(v);
      return v;
    },
  },
  methods: {
    generateColorer(value) {
      if (!value || value === this.emptyOption) {
        return () => null;
      }
      const meta = this.categoricalMetaData.find(d => d.name === value);
      const lookup = new Map(meta.levels.map(({ name, color }) => [name, color]));
      const toIndex = this.rowToIndex;
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
