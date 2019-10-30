
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
  },
  computed: {
    rowToIndex() {
      const df = this.dataset.validatedMeasurements;
      if (!df) {
        return () => -1;
      }
      const m = new Map(this.dataset.validatedMeasurements.rowNames.map((name, i) => [name, i]));
      return row => (m.has(row) ? m.get(row) : -1);
    },
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
