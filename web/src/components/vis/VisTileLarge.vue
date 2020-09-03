<script lang="ts">
import {
  PropType, defineComponent, computed, ref,
} from '@vue/composition-api';
import { analysisMap } from './analyses';
import RenderJsx from '../../utils/RenderJsx';
import { downloadSVG } from '../../utils/exporter';

export default defineComponent({
  props: {
    title: {
      type: String,
      required: true,
    },
    analysisPath: {
      type: String,
      default: '',
    },
    loading: {
      type: Boolean,
      default: false,
    },
    download: {
      default: false,
      type: Boolean,
    },
    downloadImpl: {
      default: null,
      type: Function as PropType<(arg0: HTMLElement) => {}>,
    },
  },
  components: {
    RenderJsx,
  },
  setup(props, { slots }) {
    const el = ref(document.createElement('div'));
    const hasControls = computed(() => !!slots.controls);
    const helpText = computed(() => {
      if (props.analysisPath) {
        return analysisMap[props.analysisPath].description;
      }
      return null;
    });
    function downloadImage() {
      if (props.downloadImpl) {
        props.downloadImpl(el.value);
        return;
      }
      const svg = el.value.querySelector('svg');
      if (svg) {
        downloadSVG(svg, props.title);
      }
    }
    return {
      hasControls,
      helpText,
      downloadImage,
    };
  },
});
</script>

<template>
  <v-layout
    ref="el"
    row="row"
    fill-height="fill-height"
  >
    <v-navigation-drawer
      v-if="hasControls"
      class="primary darken-3 nav-drawer"
      permanent="permanent"
      style="width: 215px;min-width: 215px;"
      touchless="touchless"
      disable-resize-watcher="disable-resize-watcher"
      stateless="stateless"
    >
      <slot name="controls" />
      <div v-if="download">
        <v-btn
          flat="flat"
          dark="dark"
          block="block"
          @click="downloadImage"
        >
          <v-icon class="mr-2">
            {{ $vuetify.icons.save }}
          </v-icon>Download PNG
        </v-btn>
      </div>
      <v-menu
        v-if="helpText"
        offset-y="offset-y"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            flat="flat"
            dark="dark"
            block="block"
            v-on="on"
          >
            <v-icon class="mr-2">
              {{ $vuetify.icons.help }}
            </v-icon>What is this?
          </v-btn>
        </template>
        <v-card max-width="300">
          <render-jsx :f="helpText" />
        </v-card>
      </v-menu>
    </v-navigation-drawer>
    <v-layout
      v-if="loading"
      justify-center="justify-center"
      align-center="align-center"
    >
      <v-progress-circular
        indeterminate="indeterminate"
        size="100"
        width="5"
      />
      <h4 class="display-1 pa-3">
        Loading...
      </h4>
    </v-layout>
    <v-layout
      v-else
      column="column"
    >
      <v-container
        class="grow-overflow ma-0 mainContainer"
        grid-list-lg="grid-list-lg"
        fluid="fluid"
      >
        <slot />
      </v-container>
    </v-layout>
  </v-layout>
</template>

<style lang="scss" scoped>
.mainContainer {
  position: relative;
}
</style>
