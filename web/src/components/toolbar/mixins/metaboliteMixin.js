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
    hideSelection: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    columnToIndex() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return () => -1;
      }
      const m = new Map(this.dataset.validatedMeasurements.columnNames.map((name, i) => [name, i]));
      return column => (m.has(column) ? m.get(column) : -1);
    },
    selectionLookup() {
      const selected = new Set((this.dataset && this.dataset.selectedColumns) || []);
      return name => selected.has(name);
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
        data: metaData.data[i],
        i,
        ...metaData.rowMetaData[i],
      })).filter(d => d.subtype === 'categorical') : [];
    },

    selectedOption() {
      return this.hideSelection ? [] : [{
        name: 'Selection',
        options: [
          {
            name: `Selected (${this.countSelected})`,
            value: 'selected',
            color: colors.selected,
          },
          {
            name: `Not Selected (${this.countNotSelected})`,
            value: 'not-selected',
            color: colors.notSelected,
          },
        ],
      }];
    },

    options() {
      return [
        ...this.selectedOption,
        ...this.categoricalMetaData.map(({ name, levels }) => ({
          name,
          options: levels.map(d => ({ name: d.label, value: d.name, color: d.color })),
        })),
      ];
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
