<script lang="ts">
import VipPlot from '@/components/vis/VipPlot.vue';
import VisTile from '@/components/vis/VisTile.vue';
import { defineComponent } from '@vue/composition-api';

export default defineComponent({
  components: {
    VipPlot,
    VisTile,
  },
  props: {
    vipScores: {
      type: Array,
      required: true,
    },
  },
});
</script>

<template>
  <vis-tile
    title="PLS-DA VIP Plot"
    svg-download
  >
    <vip-plot :vip-scores="vipScores" />
  </vis-tile>
</template>
