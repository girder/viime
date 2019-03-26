<script>
import Step from './Step.vue';

const step1 = {
  name: 'Choose data',
  description: 'Upload or select input data',
  icon: 'upload',
};
const step2 = {
  name: 'Clean Up',
  description: 'Inputation, filtering, and key selection',
  icon: 'tableEdit',
};
const step3 = {
  name: 'Transform',
  description: 'Normalize, transform, and scale your data',
  icon: 'transform',
};
const step4 = {
  name: 'Analysis',
  description: '',
  icon: 'checkedFlag',
};
const steps = [step1, step2, step3, step4];

export default {
  components: {
    Step,
  },
  props: {
    value: {
      type: Number,
      required: true,
    },
    collapsed: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return { steps };
  },
};
</script>

<template lang="pug">
v-card.stepper
  v-layout.px-4(
      row, justify-space-between,
      :class="{ 'pt-3': !collapsed, 'py-2': collapsed }")
    step(
        v-for="(step, idx) in steps",
        :key="step.name",
        :step="idx",
        :name="step.name",
        :description="step.description",
        :small="collapsed",
        :state="value - idx",
        :icon="step.icon")
  v-layout.shadow.spacers(row, :class="{ collapsed }")
    v-spacer.step-spacer(v-for="step in steps", :key="step.name")
  v-layout.shadow.expansor(row, justify-center)
    .expansor-box
      v-icon.icon(@click="$emit('update:collapsed', !collapsed)")
        | {{ collapsed ? $vuetify.icons.chevronDown : $vuetify.icons.chevronUp }}
</template>

<style lang="scss" scoped>
.stepper {
  position: relative;

  .shadow {
    position: absolute;
    width: 100%;

    &.expansor {
      bottom: 0px;

      .expansor-box {
        background-color: white;
        box-shadow: 0px 2px 2px #888888;
        border-radius: 50%;
        bottom: -12px;
        position: absolute;

        .icon {
          vertical-align: middle;
        }
      }
    }

    &.spacers {
      padding: 0 80px;
      z-index: 1;
      top: 42px;

      &.collapsed {
        top: 22px;
        padding: 0 70px;
      }

      .step-spacer {
        height: 4px;
        background-color: #ECEFF1;
      }
    }
  }
}
</style>
