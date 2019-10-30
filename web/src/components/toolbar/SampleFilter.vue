<script>
import FilterOption from './FilterOption.vue';

export default {
  components: {
    FilterOption,
  },
  props: {
    title: {
      type: String,
      required: false,
      default: 'Sample Filter',
    },
    dataset: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
    },
    value: { // {option: string | null, filter: string[], apply(index: number) => boolean}
      type: Object,
      required: false,
      default: null,
    },
  },
  computed: {
    categoricalMetaData() {
      const metaData = this.dataset.validatedSampleMetaData;
      const groups = this.dataset.validatedGroups;

      const metaDataM = metaData ? metaData.columnNames.map((name, i) => ({
        name,
        data: metaData.data.map(row => row[i]),
        i,
        ...metaData.columnMetaData[i],
      })).filter(d => d.subtype === 'categorical') : [];

      const metaGroupsM = groups ? groups.columnNames.map((name, i) => ({
        name,
        data: groups.data.map(row => row[i]),
        i,
        ...groups.columnMetaData[i],
      })).filter(d => d.levels) : [];

      return [...metaGroupsM, ...metaDataM];
    },

    options() {
      return [
        ...this.categoricalMetaData.map(({ name, levels }) => ({
          name,
          options: levels.map(d => ({ name: d.label, value: d.name, color: d.color })),
        })),
      ];
    },
    validatedValue() {
      if (this.value) {
        return this.value;
      }
      const firstOption = this.options[0];
      const v = {
        option: firstOption.name,
        filter: firstOption.options.map(d => d.value),
      };
      v.apply = this.generateFilter(v);
      return v;
    },
  },
  methods: {
    generateFilter(value) {
      if (!value.option) {
        return () => true;
      }
      const meta = this.categoricalMetaData.find(d => d.name === value.option);
      const lookup = new Set(value.filter);
      return index => lookup.has(meta.data[index]);
    },
    changeValue(value) {
      value.apply = this.generateFilter(value);
      this.$emit('input', value);
    },
  },
};
</script>

<template lang="pug">
filter-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
