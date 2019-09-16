import { CHANGE_ANALYSIS_OPTIONS } from '../../store/actions.type';
import AnalyzeWrapper from './AnalyzeWrapper.vue';
import ToolbarOption from '../utils/ToolbarOption.vue';

export function analyzeMixin(name) {
  return {
    components: {
      AnalyzeWrapper,
      ToolbarOption,
    },
    props: {
      id: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        name,
        active: true,
      };
    },
    computed: {
      ready() { return this.$store.getters.ready(this.id); },
      options() { return this.$store.getters.analysisOptions(this.id, name); },
      results() { return this.$store.getters.analysisData(this.id, name); },
      analysisState() { return this.$store.getters.analysisState(this.id, name); },
    },
    created() {
      if (this.analysisState === 'initial') {
        this.compute();
      }
    },
    activated() { this.active = true; },
    deactivated() { this.active = false; },
    watch: {
      ready() {
        this.compute();
      },
      active(val) {
        if (val) {
          this.compute();
        }
      },
    },
    methods: {
      changeOption(changes) {
        return this.$store.dispatch(CHANGE_ANALYSIS_OPTIONS, {
          dataset_id: this.id,
          name,
          changes,
        });
      },
      compute() {
        if (this.analysisState === 'initial' && this.active && this.ready) {
          // dummy change to trigger
          this.changeOption({});
        }
      },
    },
  };
}
