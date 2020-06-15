import { colors } from '../../../utils/constants';

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
    },
    selectionLast: {
      type: Boolean,
      required: false,
      default: false,
    },
    hideSelection: {
      type: Boolean,
      required: false,
      default: false,
    },
    notSelectedColor: {
      type: String,
      required: false,
      default: colors.notSelected,
    },
    emptyOption: {
      type: String,
      required: false,
      default: '',
    },
  },
  computed: {
    columnToIndex() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return () => -1;
      }
      const m = new Map(this.dataset.validatedMeasurements.columnNames.map((name, i) => [name, i]));
      return (column) => (m.has(column) ? m.get(column) : -1);
    },
    selectionLookup() {
      const selected = new Set((this.dataset && this.dataset.selectedColumns) || []);
      return (name) => selected.has(name);
    },
    countSelected() {
      return (this.dataset.selectedColumns || []).length;
    },
    countNotSelected() {
      if (!this.dataset.validatedMeasurements) {
        return 0;
      }
      return this.dataset.validatedMeasurements.columnNames.length - this.countSelected;
    },
    categoricalMetaData() {
      const metaData = this.dataset.validatedMeasurementsMetaData;

      return metaData ? metaData.rowNames.map((name, i) => ({
        name,
        value: name,
        data: metaData.data[i],
        i,
        ...metaData.rowMetaData[i],
      })).filter((d) => d.subtype === 'categorical') : [];
    },

    selectedOption() {
      return this.hideSelection ? [] : [{
        name: 'Selection',
        value: 'selection',
        options: [
          {
            name: `Selected (${this.countSelected})`,
            value: 'selected',
            color: colors.selected,
          },
          {
            name: `Not Selected (${this.countNotSelected})`,
            value: 'not-selected',
            color: this.notSelectedColor,
          },
        ],
      }];
    },

    options() {
      const metaOptions = this.categoricalMetaData.map(({ name, value, levels }) => ({
        name,
        value,
        options: levels.map((d) => ({ name: d.label, value: d.name, color: d.color })),
      }));

      const empty = this.emptyOption ? [{
        name: this.emptyOption,
        value: '',
        options: [],
      }] : [];

      if (this.selectionLast) {
        return [...empty, ...metaOptions, ...this.selectedOption];
      }
      return [...empty, ...this.selectedOption, ...metaOptions];
    },
  },
  watch: {
    dataset(newValue, oldValue) {
      const newId = newValue ? newValue.id : '';
      const oldId = oldValue ? oldValue.id : '';
      if (newId !== oldId && this.value) {
        this.$emit('input', null);
      }
    },
  },
};
