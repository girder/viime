import {
  Component, Vue, Prop, Watch,
} from 'vue-property-decorator';
import { IDataSet, ILevel } from '../../../store/model';

@Component
export default class SampleMixin extends Vue {
  @Prop({
    required: true,
  })
  readonly dataset!: IDataSet;

  @Prop({
    default: false,
  })
  readonly disabled!: boolean;

  @Prop({
    default: '',
  })
  readonly emptyOption!: string;

  @Prop()
  readonly value!: any;

  get rowToIndex() {
    const df = this.dataset.validatedMeasurements;
    if (!df) {
      return () => -1;
    }
    const m = new Map(this.dataset.validatedMeasurements.rowNames.map((name, i) => [name, i]));
    return (row: string) => (m.has(row) ? m.get(row)! : -1);
  }

  get categoricalMetaData() {
    const metaData = this.dataset.validatedSampleMetaData;
    const groups = this.dataset.validatedGroups;

    const metaDataM = metaData ? metaData.columnNames.map((name, i) => ({
      name,
      value: name,
      data: metaData.data.map(row => row[i]),
      i,
      levels: [] as ILevel[],
      ...metaData.columnMetaData[i],
    })).filter(d => d.subtype === 'categorical') : [];

    const metaGroupsM = groups ? groups.columnNames.map((name, i) => ({
      name,
      value: name,
      data: groups.data.map(row => row[i]),
      i,
      levels: [] as ILevel[],
      ...groups.columnMetaData[i],
    })).filter(d => d.levels) : [];

    return [...metaGroupsM, ...metaDataM];
  }

  get options() {
    const empty = this.emptyOption ? [{
      name: this.emptyOption,
      value: '',
      options: [],
    }] : [];
    return [
      ...empty,
      ...this.categoricalMetaData.map(({ name, value, levels }) => ({
        name,
        value,
        options: levels.map(d => ({ name: d.label, value: d.name, color: d.color })),
      })),
    ];
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
