<script lang="ts">
import { defineComponent } from '@vue/composition-api';

export default defineComponent({});
</script>

<template>
  <div>
    <p>
      This chart shows a Principal Component Analysis (PCA) scree plot. By
      default, it displays ten components.
    </p>
    <p>
      Hovering the mouse pointer over the points in the chart shows a tooltip
      displaying the eigenvalue for that component, along with the percentage of
      total variance accounted for by that component, as well as the cumulative
      percentage of total variance taken up by that component and all those
      preceding it.
    </p>
    <p>
      Vertical diagnostic cutoff lines are also plotted after the components
      providing a cumulative percentage of total variance of 50%, 80%, and 90%.
    </p>
    <p>
      The settings menu enables selection of how many principal components to
      plot, as well as whether the diagnostic cutoff lines are displayed.
    </p>
  </div>
</template>
