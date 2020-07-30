import {
  computed, Ref, ref, onActivated, onDeactivated, watchEffect,
} from '@vue/composition-api';
import store from '../../../store';
import { LOAD_PLOT } from '../../../store/actions.type';
import { SET_PLOT } from '../../../store/mutations.type';

export default function useDataPlot(id: Ref<string>, plotName: string) {
  const active = ref(true);
  const dataset = computed(() => store.getters.dataset(id.value));
  const plot = computed(() => store.getters.plot(id.value, plotName));

  // disable-eslint-next-line @typescript-eslint/no-explicit-any
  function changePlotArgs(args: any) {
    store.commit(SET_PLOT, {
      dataset_id: id.value,
      name: plotName,
      obj: { args: { ...plot.value.args, ...args } },
    });
  }

  onActivated(() => { active.value = true; });
  onDeactivated(() => { active.value = false; });
  watchEffect(() => {
    // TODO I think this is cleaner, but I'm not sure if will register properly.
    // It needs to watch for changes to plot, active, and id
    if (!plot.value.valid && !plot.value.loading && active.value) {
      store.dispatch(LOAD_PLOT, {
        dataset_id: id.value,
        name: plotName,
      });
    }
  });

  return {
    active,
    dataset,
    plot,
    changePlotArgs,
  };
}
