<script>
import { mapMutations } from 'vuex';
import { CHANGE_AXIS_LABEL, CHANGE_IMPUTATION_OPTIONS } from '@/store/actions.type';
import { SET_SELECTION } from '@/store/mutations.type';
import {
  rowMenuOptions,
  defaultRowOption,
  colMenuOptions,
  defaultColOption,
  mcar_imputation_methods,
  mnar_imputation_methods,
} from '@/utils/constants';
import { base26Converter } from '@/utils';
import SaveStatus from '@/components/SaveStatus.vue';
import CleanupTable from '@/components/Table.vue';

export default {
  components: {
    SaveStatus,
    CleanupTable,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      privateTagOptions: {
        row: rowMenuOptions,
        column: colMenuOptions,
      },
      defaultColOption,
      defaultRowOption,
      settingsDialog: false,
      mnarImputationMethods: mnar_imputation_methods,
      mcarImputationMethods: mcar_imputation_methods,
      imputation: {},
    };
  },
  computed: {
    dataset() { return this.$store.getters.dataset(this.id); },
    selected() { return this.dataset.selected; },
    radioValue() {
      const { type, ranges } = this.selected;
      const { members } = ranges;
      const types = members.map(m => this.dataset[type].labels[m]);
      const unique = [...new Set(types)];
      return unique.length === 1 ? unique[0] : null;
    },
    tagOptions() {
      return this.privateTagOptions[this.selected.type]
        .filter(option => (this.selected.ranges.members.length > 1 ? !option.mutex : true));
    },
    selectedString() {
      const { members } = this.selected.ranges;
      const multi = members.length > 1;
      if (multi) {
        return `${members.length} ${this.selected.type}s selected`;
      }
      if (this.selected.type === 'row') {
        return `Row ${members[0] + 1}`;
      }
      return `Column ${base26Converter(members[0] + 1)}`;
    },
  },
  watch: {
    dataset() {
      this.imputation.mnar = this.dataset.imputationMNAR;
      this.imputation.mcar = this.dataset.imputationMCAR;
    },
  },
  methods: {
    ...mapMutations({ setSelection: SET_SELECTION }),
    base26Converter,
    async selectOption(label) {
      const { ranges, type: context } = this.selected;
      const changes = ranges.members.map(index => ({ context, index, label }));
      await this.$store.dispatch(CHANGE_AXIS_LABEL, { dataset_id: this.id, changes });
    },
    async saveImputationSettings() {
      this.settingsDialog = false;
      await this.$store.dispatch(CHANGE_IMPUTATION_OPTIONS, {
        dataset_id: this.id,
        options: this.imputation,
      });
    },
  },
};
</script>

<template lang="pug">
v-layout.cleanup-wrapper(row)

  router-view

  v-layout(v-if="!dataset || !dataset.ready", justify-center, align-center)
    v-progress-circular(indeterminate, size="100", width="5")
    h4.display-1.pa-3 Loading Table

  v-layout(v-else, column)
    v-toolbar.radio-toolbar(dense)

      v-toolbar-title.ml-3.radio-title
        .subheading.font-weight-bold.primary--text.text--lighten-1  SELECT DATA TYPE
        .primary--text.text--darken-3.body-2(style="margin-top: -8px;") {{ selectedString }}
      v-divider.mx-2(vertical, inset)
      v-radio-group.mx-2.radio-group(mandatory, row, hide-details,
          :value="radioValue",
          @change="selectOption")
        v-radio.my-1(v-for="option in tagOptions",
            color="primary darken-3",
            :value="option.value",
            :label="option.title",
            :key="option.value")
          template(#label)
            span {{ option.title }}
            v-icon.radio-icon.mdi-light(small, :class="option.color")
              | {{ $vuetify.icons[option.icon] }}

      v-spacer

      save-status
      v-dialog(v-model="settingsDialog", max-width="500")
        template(v-slot:activator="{ on }")
          v-btn(icon, v-on="on")
            v-icon {{ $vuetify.icons.settings }}
        v-card
          v-card-title.headline Imputation Settings
          v-card-text
            v-select(
                item-value="value",
                item-text="label",
                :items="mnarImputationMethods",
                label="MNAR imputation method",
                v-model="imputation.mnar")
            v-select(
                item-value="value",
                item-text="label",
                :items="mcarImputationMethods",
                label="MCAR imputation method",
                v-model="imputation.mcar")
          v-card-actions
            v-spacer
            v-btn(flat, @click="settingsDialog = false") Close
            v-btn(flat, @click="saveImputationSettings") Save
      v-icon {{ $vuetify.icons.download }}

    .overflow-auto
      cleanup-table(v-bind="{ dataset, id, selected }", @setSelection="setSelection")
</template>

<style lang="scss">
.cleanup-wrapper {
  width: 100%;

  .radio-toolbar {
    .v-toolbar__content {
      height: inherit !important;
      padding: 0px;
    }

    .v-input--selection-controls__input {
      margin-right: 2px;
    }

    .radio-group {
      padding-top: 0px;
    }

    .v-radio {
      border-radius: 3px;
      padding: 2px;
      background-color: #dde0e1; // TODO: find a better way to get this color.

      .v-label {
        color: var(--v-primary-darken3);
      }
    }

    .radio-title {
      min-width: 110px;
    }

    .v-divider {
      height: 32px;
    }

    .radio-icon {
      padding: 2px;
      border-radius: 3px;
      margin: 4px;
    }
  }
}

</style>
