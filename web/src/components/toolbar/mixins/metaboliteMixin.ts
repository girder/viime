import {
  Component, Vue, Prop, Watch,
} from 'vue-property-decorator';
import { colors } from '../../../utils/constants';
import { IDataSet, ILevel } from '../../../store/model';

@Component
export default class MetaboliteMixin extends Vue {
  @Prop({
    required: true,
  })
  readonly dataset!: IDataSet;

  @Prop({
    default: false,
  })
  readonly disabled!: boolean;

  @Prop({
    default: false,
  })
  readonly selectionLast!: boolean;

  @Prop({
    default: false,
  })
  readonly hideSelection!: boolean;

  @Prop({
    default: colors.notSelected,
  })
  readonly notSelectedColor!: string;

  @Prop({
    default: '',
  })
  readonly emptyOption!: string;

  @Prop()
  readonly value!: any;

  get columnToIndex() {
    const df = this.dataset.validatedMeasurements;
    if (!df) {
      return () => -1;
    }
    const m = new Map(this.dataset.validatedMeasurements.columnNames.map((name, i) => [name, i]));
    return (column: string) => (m.has(column) ? m.get(column)! : -1);
  }

  get selectionLookup() {
    const selected = new Set((this.dataset && this.dataset.selectedColumns) || []);
    return (name: string) => selected.has(name);
  }

  get countSelected() {
    return (this.dataset.selectedColumns || []).length;
  }

  get countNotSelected() {
    if (!this.dataset.validatedMeasurements) {
      return 0;
    }
    return this.dataset.validatedMeasurements.columnNames.length - this.countSelected;
  }

  get categoricalMetaData() {
    const metaData = this.dataset.validatedMeasurementsMetaData;

    return metaData ? metaData.rowNames.map((name, i) => ({
      name,
      value: name,
      data: metaData.data[i],
      i,
      levels: [] as ILevel[],
      ...metaData.rowMetaData[i],
    })).filter(d => d.subtype === 'categorical') : [];
  }

  get selectedOption() {
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
  }

  get options() {
    const metaOptions = this.categoricalMetaData.map(({ name, value, levels }) => ({
      name,
      value,
      options: levels.map(d => ({ name: d.label, value: d.name, color: d.color })),
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
  }

  @Watch('dataset')
  watchDataset(newValue: IDataSet, oldValue: IDataSet) {
    const newId = newValue ? newValue.id : '';
    const oldId = oldValue ? oldValue.id : '';
    if (newId !== oldId && this.value) {
      this.$emit('input', null);
    }
  }
}
