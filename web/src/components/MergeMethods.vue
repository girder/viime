<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import HelpDialog from './toolbar/HelpDialog.vue';

export const DEFAULT_MERGE_METHOD = 'multi_block';

@Component({
  components: {
    HelpDialog,
  },
})
export default class MergeMethods extends Vue {
  @Prop({
    default: null,
  })
  readonly value!: string;

  get method() {
    return this.value;
  }

  set method(value: string) {
    this.$emit('input', value);
  }
}
</script>
<template lang="pug">
v-radio-group(v-model="method", label="Merge Method")
  v-radio(value="multi_block")
    template(#label)
      | Multiblock Data Fusion
      help-dialog(title="Multiblock Data Fusion", outline)
        p
          | This method normalizes each of the individual data sets so that their first
          | principal component has the same length (as measured by the first singular value of
          | each data table) and then to combine these data tables to a grand table.
          | PCA is then performed on the concatenated table.
        cite
          a(href="https://doi.org/10.1002/wics.1246",
              target="_blank", rel="noopener noreferrer")
            | Abdi H, Williams LJ, Dominique V.: Multiple factor analysis: principal component
            |  analysis for multitable and multiblock data sets. WIREs Comput Stat 2013.
  v-radio(value="clean")
    template(#label)
      | Mid-level data fusion approach
      help-dialog(title="Mid-level data fusion approach", outline)
        p
          | This method concatenates the normalized scores of PCAs applied to each data set.
          | In this way, all variables are kept avoiding any loss of information and only
          | common major effects are observed. PCA is then performed on the concatenated table.
        cite
          a(href="https://doi.org/10.1007/s00216-016-9538-4",
              target="_blank", rel="noopener noreferrer")
            | Spiteri M, Dubin E, Cotton J et al.:
            | Data fusion between high resolution 1H-NMR and mass spectrometry: a synergetic
            | approach to honey botanical origin characterization.
            | Anal Bioanal Chem (2016) 408: 4389.
  v-radio(value="simple")
    template(#label)
      | Simple data fusion
      help-dialog(title="Simple data fusion", outline)
        p
          | This method concatenates the raw data of the data sets.
          | PCA is then performed on the concatenated table
</template>
