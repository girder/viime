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
      default: 'Metabolite Filter',
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
    countSelected() {
      return (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.dataset.validatedMeasurements) {
        return 0;
      }
      return this.dataset.validatedMeasurements.columnNames.length - this.countSelected;
    },
    options() {
      // const selected = new Set(this.dataset.selectedColumns || []);
      const metaData = this.dataset.validatedMeasurementsMetaData;

      const cats = metaData ? metaData.rowNames.map((name, i) => ({
        name,
        ...metaData.rowMetaData[i],
      })).filter(d => d.subtype === 'categorical') : [];

      return [
        {
          name: 'Selection',
          options: [
            {
              name: `Selected (${this.countSelected})`,
              value: 'selected',
            },
            {
              name: `Not Selected (${this.countNotSelected})`,
              value: 'not-selected',
            },
          ],
        },
        ...cats.map(({ name, levels }) => ({
          name,
          options: levels.map(d => ({ name: d.label, value: d.name })),
        })),
      ];
    },
    validatedValue() {
      if (this.value) {
        return this.value;
      }
      return {
        option: null,
        filter: [],
        apply: () => true,
      };
    },
  },
  methods: {
    changeValue(value) {
      // TODO right filter function
      value.apply = () => true;
      this.$emit('input', value);
    },
  },
};
</script>

<template lang="pug">
filter-option(:title="title", :disabled="disabled",
    :options="options", :value="validatedValue", @input="changeValue($event)")
</template>
