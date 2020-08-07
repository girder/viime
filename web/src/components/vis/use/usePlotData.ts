import {
  computed, Ref, ref, onActivated, onDeactivated, watchEffect,
} from '@vue/composition-api';
import store from '../../../store';
import { LOAD_PLOT } from '../../../store/actions.type';
import { SET_PLOT } from '../../../store/mutations.type';

export default function usePlotData(id: Ref<string>, plotName: string) {
  const active = ref(true);
  const dataset = computed(() => store.getters.dataset(id.value));
  const plot = computed(() => store.getters.plot(id.value, plotName));

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
    const plotValue = plot.value;
    const activeValue = active.value;
    const idValue = id.value;
    if (!plotValue.valid && !plotValue.loading && activeValue) {
      store.dispatch(LOAD_PLOT, {
        dataset_id: idValue,
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
