import { mapState, mapActions } from 'vuex';
import { load_dataset } from '../store';
import { LOAD_PLOT } from '../store/actions.type';

/**
 * Load dataset from server for any view where
 * dataset_id is defined
 */
const loadDataset = {
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  computed: {
    datasetLoaded() {
      return !!this.$store.state.datasets[this.id];
    },
  },
  created() {
    const dataset = this.$store.getters.dataset(this.id);
    if (!dataset) {
      load_dataset(this.$store, { dataset_id: this.id });
    }
  },
};

/**
 * Expects `id` to exist on the wrapping component
 * @param {String} plotName name of the plot to subscribe to
 */
const plotDataMixin = plotName => ({
  data() {
    return {
      active: true,
    };
  },
  activated() { this.active = true; },
  deactivated() { this.active = false; },
  mounted() { this.reloadPlot(); },
  computed: {
    ...mapState(['loading']),
    dataset() { return this.$store.getters.dataset(this.id); },
    plot() { return this.$store.getters.plot(this.id, plotName); },
  },
  watch: {
    // eslint-disable-next-line func-names
    'plot.valid': function () { this.reloadPlot(); },
    id() { this.reloadPlot(); },
    active(val) {
      if (val) {
        this.reloadPlot();
      }
    },
  },
  methods: {
    ...mapActions({ loadPlot: LOAD_PLOT }),
    reloadPlot() {
      if (!this.plot.valid && this.active) {
        this.loadPlot({
          dataset_id: this.id,
          name: plotName,
        });
      }
    },
  },
});

export {
  loadDataset,
  plotDataMixin,
};
