import { LOAD_DATASET } from '../store/actions.type';

/**
 * Load dataset from server for any view where
 * dataset_id is defined
 */
const loadDataset = {
  data() {
    return {
      loaded: !!this.$store.state.datasets[this.id],
    };
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
