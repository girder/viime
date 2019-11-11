import { mapActions, mapMutations } from 'vuex';
import { LOAD_PLOT } from '../../../store/actions.type';
import { SET_PLOT } from '../../../store/mutations.type';

/**
 * Expects `id` to exist on the wrapping component
 * @param {String} plotName name of the plot to subscribe to
 */
export default function (plotName) {
  return {
    data() {
      return {
        active: true,
      };
    },
    activated() { this.active = true; },
    deactivated() { this.active = false; },
    mounted() { this.reloadPlot(); },
    computed: {
      dataset() { return this.$store.getters.dataset(this.id); },
      plot() { return this.$store.getters.plot(this.id, plotName); },
    },
    watch: {
      'plot.valid': function f() { this.reloadPlot(); },
      id() { this.reloadPlot(); },
      active(val) {
        if (val) {
          this.reloadPlot();
        }
      },
    },
    methods: {
      ...mapActions({ loadPlot: LOAD_PLOT }),
      ...mapMutations({ setPlot: SET_PLOT }),
      changePlotArgs(args) {
        this.setPlot({
          dataset_id: this.id,
          name: plotName,
          obj: { loading: false, valid: false, args: { ...this.plot.args, ...args } },
        });
      },
      reloadPlot() {
        if (!this.plot.valid && this.active) {
          this.loadPlot({
            dataset_id: this.id,
            name: plotName,
          });
        }
      },
      getPlotDataProperty(property, dflt) {
        if (this.plot && this.plot.data !== null) {
          return this.plot.data[property];
        }
        return dflt === undefined ? null : dflt;
      },
    },
  };
}
