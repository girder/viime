<script>
import { mapState } from 'vuex';

export default {
  computed: {
    ...mapState(['loading', 'saving', 'lasterror']),
  },
};
</script>

<template lang="pug">
.save-status-component
  v-tooltip(left)
    template(v-slot:activator="{ on }")
      div(v-on="on")
        v-icon.save(v-if="saving") {{ $vuetify.icons.save }}
        v-progress-circular(v-else-if="loading", indeterminate)
        v-icon(v-else-if="lasterror", color="error") {{ $vuetify.icons.warningCircle }}
        v-icon.sync(v-else) {{ $vuetify.icons.save }}

    span(v-if="saving") Saving...
    span(v-else-if="loading") Loading...
    span(v-else-if="lasterror") {{ lasterror }}
    span(v-else) In sync with the server
</template>

<style lang="scss" scoped>
.save-status {
  span {
    text-decoration: none;
  }

  &.dark {
    color: white;
  }
}

@keyframes save_animation {
  0% { transform: scale(1); }
  25% { transform: scale(1.15); }
  50% { transform: scale(1); }
  75% { transform: scale(0.85); }
  100% { transform: scale(1); }
}

.save {
  transition: opacity .5s ease;
  opacity: 1;
  animation-name: save_animation;
  animation-duration: 2s;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}

.sync {
  transition: opacity .5s ease;
  opacity: 0.2;
}
</style>
