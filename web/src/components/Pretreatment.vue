<script>
import { SET_SELECTION } from '@/store/mutations.type';
import { loadDataset } from '@/utils/mixins';
import { analyses } from '.';

export default {
  mixins: [loadDataset],
  props: {
    problem: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      datasets: this.$store.state.datasets,
      analyses,
    };
  },
  methods: {
    valid(dataset) {
      return this.$store.getters.valid(dataset.id);
    },
    navigate(dataset) {
      const { id } = dataset;
      const name = this.valid(dataset)
        ? this.$router.currentRoute.name
        : 'Cleanup Data';
      this.$router.push({
        name,
        params: { id },
      });
    },
    problemNav(problem) {
      if (problem.multi) {
        this.$router.push({ path: `/pretreatment/${this.id}/cleanup/${problem.type}` });
      } else {
        this.$router.push({ path: `/pretreatment/${this.id}/cleanup` });
        this.$store.commit(SET_SELECTION, {
          key: this.id,
          event: {},
          axis: problem.context,
          idx: problem[`${problem.context}_index`],
        });
      }
    },
    isSubRoute(dataset, start) {
      return this.$router.currentRoute.path.startsWith(`/pretreatment/${dataset.id}/${start}`);
    },
  },
};
</script>

<template lang="pug">
v-layout.pretreatment-component(row, fill-height)

  v-navigation-drawer.navigation(floating, permanent, style="min-width: 220px; width: 220px;")
    v-layout(column, fill-height)
      v-list.pt-0
        v-list-group(v-for="(dataset, index) in datasets",
            :key="dataset.id",
            :value="dataset.id === id",
            :append-icon="null",
            @click="navigate(dataset)")
          template(v-slot:activator)
            v-list-tile.file-name
              v-list-tile-title.title {{ dataset.name }}
              v-list-tile-action(v-if="dataset.validation.length")
                v-icon.pr-1(color="warning") {{ $vuetify.icons.warning }}
              v-list-tile-action(v-else)
                v-icon.pr-1(color="success") {{ $vuetify.icons.check }}
          v-list.view-list

            v-list-tile.ml-2(
                :class="{ active: $router.currentRoute.name === 'Cleanup Data' }",
                @click="$router.push({ path: `/pretreatment/${dataset.id}/cleanup` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.tableEdit }}
                | Clean Up Table

            v-list-tile.ml-4.my-1.px-0.small-tile(v-for="problemData in dataset.validation",
                @click="problemNav(problemData)",
                :class="{ active: problemData.type === problem }",
                :inactive="!problemData.clickable",
                :key="problemData.title")
              v-list-tile-title.small-tile.px-0
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
                :disabled="!valid(dataset)",
                @click="$router.push({ path: `/pretreatment/${dataset.id}/transform` })")
              v-list-tile-title.pl-2
                v-icon.pr-1.middle {{ $vuetify.icons.bubbles }}
                | Transform Table

            v-list-group.ml-2.link-group(
                :append-icon="null",
                :value="isSubRoute(dataset, `analyze/`)",
                :disabled="!valid(dataset)",
                @click="$router.push({ path: `/pretreatment/${dataset.id}/analyze` })")
              template(v-slot:activator)
                v-list-tile(
                   :class="{ active: $router.currentRoute.name === 'Analyze Data' }")
                  v-list-tile-title.pl-2
                    v-icon.pr-1.middle {{ $vuetify.icons.cogs }}
                    | Analyze Table
              v-list-tile.ml-2.small-tile(
                  v-for="a in analyses", :key="a.path",
                  :class="{ active: $router.currentRoute.name === a.shortName }",
                  @click="$router.push({ path: `/pretreatment/${dataset.id}/analyze/${a.path}` })")
                v-list-tile-title.pl-2
                  v-icon.pr-1.middle {{ $vuetify.icons.compare }}
                  | {{a.shortName}}

  keep-alive
    router-view
</template>

<style lang="scss">
.pretreatment-component .navigation {
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
  .file-name .v-list__tile {
    padding-right: 0;

    .v-list__tile__action{
      min-width: 0;
      padding-right: 16px;
    }
  }

  .view-list .v-list__tile--link,
  .view-list .link-group > .v-list__group__header {
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
