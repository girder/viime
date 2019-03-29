<script>
import { loadDataset } from '@/utils/mixins';

export default {
  mixins: [loadDataset],
  data() {
    return {
      dataset_id: this.$router.currentRoute.params.id,
      datasets: this.$store.state.datasets,
    };
  },
  methods: {
    navigate(id) {
      this.$router.push({
        name: this.$router.currentRoute.name,
        params: { id },
      });
    },
  },
};
</script>

<template lang="pug">
v-layout.pretreatment(row, fill-height)
  v-navigation-drawer.navigation(permanent, style="width: 200px; min-width: 260px;")
    v-layout(column, fill-height)
      v-list.pt-0
        v-list-group(v-for="(dataset, index) in datasets",
            :key="dataset.source.id",
            :value="dataset.visible",
            @click="navigate(dataset.source.id)")
          template(v-slot:activator)
            v-list-tile
              v-list-tile-title {{ dataset.source.name }}
          v-list.view-list
            v-list-tile.ml-2(
                :class="{ active: $router.currentRoute.name === 'Cleanup Data' }",
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/cleanup` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.tableEdit }}
                | Clean Up Table
            v-list-tile.ml-4.my-1.small-tile(@click="")
              v-list-tile-title.small-tile.pl-2
                v-icon.pr-1.middle(color="error") {{ $vuetify.icons.close }}
                | Missing data (12)
            v-list-tile.ml-4.my-1.small-tile(@click="")
              v-list-tile-title.small-tile.pl-2
                v-icon.pr-1.middle(color="warning") {{ $vuetify.icons.alert }}
                | Low Variance (8)
            v-list-tile.ml-2(
                :class="{ active: $router.currentRoute.name === 'Transform Data' }",
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/transform` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.bubbles }}
                | Transform Table
      v-spacer
      v-btn.accent Next
  v-layout
    router-view(:dataset-id="$router.currentRoute.params.id")
</template>

<style lang="scss">
.pretreatment .navigation {
  i.middle {
    vertical-align: top;
  }
  .small-tile a {
    height: 32px;
  }

  .active {
    background-color: #263238;
    border-radius: 40px 0 0 40px;
    color: white;
    i {
      color: white;
    }
  }
  .view-list .v-list__tile--link {
    transition: none;

    .v-list__tile__title {
      transition: none;
    }

    &:hover {
      border-radius: 40px 0 0 40px;
    }
  }
}

</style>
