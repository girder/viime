import {
  PropType, computed, watch, Ref, ref,
} from '@vue/composition-api';
import { colors } from '../../../utils/constants';

// TODO this is a subset of a type from Vuex
interface Dataset {
  id: string;
  validatedMeasurements: {
    columnNames: string[];
  };
  validatedMeasurementsMetaData: {
    data: string[][];
    rowMetaData: Array<{
      subtype: string;
      levels: Array<{
        label: string;
        name: string;
        color: string;
      }>;
    }>;
    rowNames: string[];
  };
  selectedColumns: string[];
}

export const metaboliteProps = {
  dataset: {
    type: Object as PropType<Dataset>,
    required: true,
    default: null, // required for dataset to be non-optional
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
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
};

export default function useMetabolite({
  dataset,
  selectionLast = ref(false),
  hideSelection = ref(false),
  notSelectedColor = ref(colors.notSelected),
  emptyOption = ref(''),
}: {
  dataset: Ref<Dataset>;
  selectionLast: Ref<boolean>;
  hideSelection: Ref<boolean>;
  notSelectedColor: Ref<string>;
  emptyOption: Ref<string>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
}, { emit }: { emit: (event: string, ...args: any[]) => void }) {
  const columnToIndex = computed(() => {
    const df = dataset.value.validatedMeasurements;
    if (!df) {
      return () => -1;
    }
    const m = new Map(dataset.value.validatedMeasurements.columnNames.map((name, i) => [name, i]));
    return (column: string) => (m.has(column) ? m.get(column) as number : -1);
  });
  const selectionLookup = computed(() => {
    const selected = new Set(dataset.value.selectedColumns || []);
    return (name: string) => selected.has(name);
  });
  const countSelected = computed(() => (dataset.value.selectedColumns || []).length);
  const countNotSelected = computed(() => {
    if (!dataset.value.validatedMeasurements) {
      return 0;
    }
    return dataset.value.validatedMeasurements.columnNames.length - countSelected.value;
  });
  const categoricalMetaData = computed(() => {
    const metaData = dataset.value.validatedMeasurementsMetaData;

    return metaData ? metaData.rowNames.map((name, i) => ({
      name,
      value: name,
      data: metaData.data[i],
      i,
      ...metaData.rowMetaData[i],
    })).filter((d) => d.subtype === 'categorical') : [];
  });
  const selectedOption = computed(() => (hideSelection.value ? [] : [{
    name: 'Selection',
    value: 'selection',
    options: [
      {
        name: `Selected (${countSelected.value})`,
        value: 'selected',
        color: colors.selected,
      },
      {
        name: `Not Selected (${countNotSelected.value})`,
        value: 'not-selected',
        color: notSelectedColor.value,
      },
    ],
  }]));
  const options = computed(() => {
    const metaOptions = categoricalMetaData.value.map(({ name, value, levels }) => ({
      name,
      value,
      options: levels.map((d) => ({ name: d.label, value: d.name, color: d.color })),
    }));

    const empty = emptyOption.value ? [{
      name: emptyOption.value,
      value: '',
      options: [],
    }] : [];

    if (selectionLast.value) {
      return [...empty, ...metaOptions, ...selectedOption.value];
    }
    return [...empty, ...selectedOption.value, ...metaOptions];
  });
  watch(dataset, (newValue, oldValue) => {
    const newId = newValue?.id || '';
    const oldId = oldValue?.id || '';
    if (newId !== oldId) {
      emit('input', null);
    }
  });

  return {
    columnToIndex,
    selectionLookup,
    countSelected,
    countNotSelected,
    categoricalMetaData,
    selectedOption,
    options,
  };
}
