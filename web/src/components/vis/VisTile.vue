<script>
import { format } from 'd3-format';
import { downloadSVG } from '../../utils/exporter';

export default {
  props: {
    title: {
      type: String,
      default: '',
    },
    loading: {
      default: false,
      type: Boolean,
    },
    svgDownload: {
      default: false,
      type: Boolean,
    },
  },

  data() {
    return {
      scales: [
        { scaleFactor: 0.5, cssClass: 'span1' },
        { scaleFactor: 1, cssClass: 'span2' },
        { scaleFactor: 1.5, cssClass: 'span3' },
        { scaleFactor: 2, cssClass: 'span4' },
        { scaleFactor: 2.5, cssClass: 'span5' },
      ],
      scaleIndex: 1,
    };
  },

  computed: {
    scaleClass() {
      return this.scales[this.scaleIndex].cssClass;
    },
    scaleFactor() {
      return this.scales[this.scaleIndex].scaleFactor;
    },
    scaleOptions() {
      const f = format('.0%');
      return this.scales.map((d, i) => ({ text: f(d.scaleFactor), value: i }));
    },
  },

  methods: {
    setScaleIndex(value) {
      this.scaleIndex = Math.max(Math.min(Number.parseInt(value, 10), this.scales.length - 1), 0);
    },
    downloadSVG() {
      const svg = this.$el.querySelector('svg');
      if (svg) {
        downloadSVG(svg, this.title);
      }
    },
  },
};
</script>

<template lang="pug">
v-flex.white.rounded.main(shrink=1, :class="scaleClass")
  v-toolbar.primary.darken-3.top-rounded(dark, flat, dense)
    v-toolbar-title {{ title }}
    v-spacer
    v-toolbar-items
      v-btn(@click="setScaleIndex(scaleIndex - 1)", :disabled="scaleIndex === 0", icon)
        v-icon {{ $vuetify.icons.magnifyMinus }}
      v-select.scaleFactor(:value="scaleIndex", @change="setScaleIndex($event)",
          :items="scaleOptions", hide-details, item-text="text", item-value="value")
      v-btn(@click="setScaleIndex(scaleIndex + 1)",
          :disabled="scaleIndex === scales.length - 1", icon)
        v-icon {{ $vuetify.icons.magnifyPlus }}
      v-btn(v-if="svgDownload", @click="downloadSVG", icon)
        v-icon {{ $vuetify.icons.save }}
      slot(name="controls")
  v-progress-linear.ma-0.progress(v-if="loading", indeterminate, height=4)
  v-card.bottom-rounded.content(flat)
    slot
</template>

<style scoped lang="scss">
.span1 {
  grid-column: span 1;
  grid-row: span 1;
}
.span2 {
  grid-column: span 2;
  grid-row: span 2;
}
.span3 {
  grid-column: span 3;
  grid-row: span 3;
}
.span4 {
  grid-column: span 4;
  grid-row: span 4;
}
.span5 {
  grid-column: span 5;
  grid-row: span 5;
}
.span6 {
  grid-column: span 6;
  grid-row: span 6;
}
.span7 {
  grid-column: span 7;
  grid-row: span 7;
}
.span8 {
  grid-column: span 8;
  grid-row: span 8;
}

.scaleFactor {
  max-width: 4em;
}

.main {
  position: relative;
  display: flex;
  flex-direction: column;
}
.rounded {
  border-radius: 5px;
}

.top-rounded {
  border-radius: 5px 5px 0 0;
}

.bottom-rounded {
  border-radius: 0 0 5px 5px;
}


.progress {
  position: absolute;
}
</style>

<style scoped>

.content {
  flex: 1 1 0;
  display: flex;
  flex-direction: column
}

.content >>> > * {
  flex: 1 1 0;
  overflow: hidden;
}
</style>
