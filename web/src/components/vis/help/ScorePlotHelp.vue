<script lang="ts">
import { defineComponent } from '@vue/composition-api';

export default defineComponent({});
</script>

<template>
  <div>
    <p>
      This chart shows Principal Component Analysis (PCA) scores as a scatter plot.
      When the chart first appears, it displays the first two principal components
      on the x and y axes.
    </p>
    <p>
      The dataset's group column is used to partition the observations into groups
      by color; each group's data points are plotted along with a confidence ellipse
      illustrating one standard deviation in the group's primary and secondary
      directions.
    </p>
    <p>
      The control panel contains a few settings you can use to change how the PCA
      score data is displayed: the number fields allow you to choose which two PCs
      are plotted, while the toggle switch enables turning the confidence ellipses
      on and off. As the PCs are changed, note that the percent of total variance
      accounted for by each component is displayed within the axis label.
    </p>
  </div>
</template>
