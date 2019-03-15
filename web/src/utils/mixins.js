import { LOAD_DATASET } from '../store/actions.type';

/**
 * Load dataset from server for any view where
 * dataset_id is defined
 */
const loadDataset = {
  created() {
    this.$store.dispatch(LOAD_DATASET, { dataset_id: this.dataset_id });
  },
};

export {
  loadDataset,
};
