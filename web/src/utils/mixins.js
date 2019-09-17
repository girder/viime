import { load_dataset } from '../store';

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

export {
  loadDataset,
};
