<script lang="ts">
import { defineComponent } from '@vue/composition-api';

export default defineComponent({});
</script>

<template>
  <div>
    <p>
      This chart shows a Principal Component Analysis (PCA) loadings plot. The
      Pearson correlation of each metabolite with the displayed principal
      components is plotted in a scatter plot. A reticle appears at the origin
      for help in interpreting the plotted points as vectors.
    </p>
    <p>
      Hovering the mouse pointer over a point shows the name of the metabolite,
      as well as exact values for correlation with the two principal components.
    </p>
    <p>
      The menu contains options for selecting which components to show in the
      plot, as well as a toggle for turning the reticle display on and off.
    </p>
  </div>
</template>
