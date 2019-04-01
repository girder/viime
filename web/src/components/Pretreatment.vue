<script>
import { loadDataset } from '@/utils/mixins';

export default {
  mixins: [loadDataset],
  props: {
    id: {
      type: String,
      required: true,
    },
    problem: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
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
    problemNav(problem) {
      if (problem.data) {
        this.$router.push({
          path: `/pretreatment/${this.id}/cleanup/${problem.type}`,
        });
      }
    },
  },
};
</script>

<template lang="pug">
v-layout.pretreatment(row, fill-height)

  v-navigation-drawer.navigation(floating, permanent, style="min-width: 240px; width: 240px;")
    v-layout(column, fill-height)
      v-list.pt-0
        v-list-group(v-for="(dataset, index) in datasets",
            :key="dataset.source.id",
            :value="dataset.visible",
            @click="navigate(dataset.source.id)")
          template(v-slot:activator)
            v-list-tile
              v-list-tile-title.title {{ dataset.source.name }}
          v-list.view-list

            v-list-tile.ml-2(
                :class="{ active: $router.currentRoute.name === 'Cleanup Data' }",
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/cleanup` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.tableEdit }}
                | Clean Up Table

            v-list-tile.ml-4.my-1.small-tile(v-for="problemData in dataset.validation",
                @click="problemNav(problemData)",
                :class="{ active: problemData.type === problem }",
                :inactive="!problemData.data",
                :key="problemData.title")
              v-list-tile-title.small-tile.pl-2
                v-icon.pr-1.middle(
                    :color="problemData.severity") {{ $vuetify.icons[problemData.severity] }}
                | {{ problemData.title }}
                span.pl-1(v-if="problemData.data") ({{ problemData.data.length }})
                v-tooltip(v-else, top)
                  template(v-slot:activator="{ on }")
                    v-icon.pl-1(small, @click="", v-on="on") {{ $vuetify.icons.info }}
                  span {{ problemData.description }}

            v-list-tile.ml-2(
                :class="{ active: $router.currentRoute.name === 'Transform Data' }",
                @click="$router.push({ path: `/pretreatment/${dataset.source.id}/transform` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.bubbles }}
                | Transform Table
      v-spacer
      v-btn.accent Next

  router-view
</template>

<style lang="scss">
.pretreatment .navigation {
  i.middle {
    vertical-align: top;
  }
  .small-tile .v-list__tile {
    height: 32px;
  }

  .active {
    background-color: #37474f;
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
