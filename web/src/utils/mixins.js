import { LOAD_DATASET } from '../store/actions.type';

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
      this.$store.dispatch(LOAD_DATASET, { dataset_id: this.id });
    }
  },
};

export {
  loadDataset,
};
