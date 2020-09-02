import {
  watch, computed, Ref, ref, PropType,
} from '@vue/composition-api';

// TODO this is a subset of a type from Vuex
interface Dataset {
  id: string;
  validatedMeasurements: {
    rowNames: string[];
  };
  validatedSampleMetaData: {
    columnNames: string[];
    data: string[][];
    columnMetaData: Array<{
      levels: Array<{
        color: string;
        description: string;
        label: string;
        name: string;
      }>;
      subtype: string;
    }>;
  };
  validatedGroups: {
    columnNames: string[];
    data: string[][];
    columnMetaData: Array<{
      levels: Array<{
        color: string;
        description: string;
        label: string;
        name: string;
      }>;
      subtype: string;
    }>;
  };
}

export const sampleProps = {
  dataset: {
    type: Object as PropType<Dataset>,
    required: true,
    default: null,
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
  emptyOption: {
    type: String,
    required: false,
    default: '',
  },
};

export default function useSample({
  dataset,
  emptyOption = ref(''),
}: {
  dataset: Ref<Dataset>;
  emptyOption: Ref<string>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
}, { emit }: { emit: (event: string, ...args: any[]) => void }) {
  const rowToIndex = computed(() => {
    const df = dataset.value.validatedMeasurements;
    if (!df) {
      return () => -1;
    }
    const m = new Map(dataset.value.validatedMeasurements.rowNames.map((name, i) => [name, i]));
    return (row: string) => (m.has(row) ? m.get(row) as number : -1);
  });
  const categoricalMetaData = computed(() => {
    const metaData = dataset.value.validatedSampleMetaData;
    const groups = dataset.value.validatedGroups;

    const metaDataM = metaData ? metaData.columnNames.map((name, i) => ({
      name,
      value: name,
      data: metaData.data.map((row) => row[i]),
      i,
      ...metaData.columnMetaData[i],
    })).filter((d) => d.subtype === 'categorical') : [];

    const metaGroupsM = groups ? groups.columnNames.map((name, i) => ({
      name,
      value: name,
      data: groups.data.map((row) => row[i]),
      i,
      ...groups.columnMetaData[i],
    })).filter((d) => d.levels) : [];

    return [...metaGroupsM, ...metaDataM];
  });

  const options = computed(() => {
    const empty = emptyOption.value ? [{
      name: emptyOption.value,
      value: '',
      options: [],
    }] : [];
    return [
      ...empty,
      ...categoricalMetaData.value.map(({ name, value, levels }) => ({
        name,
        value,
        options: levels.map((d) => ({ name: d.label, value: d.name, color: d.color })),
      })),
    ];
  });
  watch(dataset, (newValue, oldValue) => {
    const newId = newValue?.id || '';
    const oldId = oldValue?.id || '';
    if (newId !== oldId) {
      emit('input', null);
    }
  });
  return {
    rowToIndex,
    categoricalMetaData,
    options,
  };
}
