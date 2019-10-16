<script>
import { SET_SELECTION } from '@/store/mutations.type';
import { loadDataset } from '@/utils/mixins';
import analyses from './vis/analyses';

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
    stopPropagation(evt) {
      evt.stopPropagation();
    },
    valid(dataset) {
      return this.$store.getters.valid(dataset.id);
    },
    navigate(evt, dataset) {
      evt.preventDefault();
      evt.stopPropagation();
      const { id } = dataset;
      this.$router.push({
        name: 'Pretreat Data',
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
    v-list(dense)
      v-list-group(v-for="(dataset, index) in datasets",
          :key="dataset.id",
          :value="dataset.id === id")
        template(#activator)
          v-list-tile(:to="{ name: 'Pretreat Data', params: { id: dataset.id } }",
              @click="stopPropagation")
              v-list-tile-title
                v-icon(color="warning", v-if="dataset.validation.length") {{ $vuetify.icons.warning }}
                v-icon(color="success", v-else) {{ $vuetify.icons.check }}
                | {{ dataset.name }}

        v-list-tile(:to="{ name: 'Clean Up Table' }")
          v-list-tile-title
            v-icon.drawericon {{ $vuetify.icons.tableEdit }}
            | Clean Up Table

        v-list-tile.small-tile(v-for="problemData in dataset.validation",
            @click="problemNav(problemData)",
            :class="{ active: problemData.type === problem }",
            :inactive="!problemData.clickable",
            :key="problemData.title")
          v-list-tile-title
            v-icon.drawericon(
                :color="problemData.severity") {{ $vuetify.icons[problemData.severity] }}
            | {{ problemData.title }}
            span(v-if="problemData.data") ({{ problemData.data.length }})
            v-tooltip(v-else, top)
              template(#activator="{ on }")
                v-icon(small, @click="", v-on="on") {{ $vuetify.icons.info }}
              span {{ problemData.description }}

        v-list-tile(:to="{ name: 'Transform Table' }",
            :disabled="!valid(dataset)")
          v-list-tile-title
            v-icon.pr-1.drawericon {{ $vuetify.icons.bubbles }}
            | Transform Table

        v-list-group(sub-group,
            :disabled="!valid(dataset)",
            group=".*/analyze/.*"
            :value="true")
          template(#activator)
            v-list-tile(:to="{ name: 'Analyze Data' }",
              @click="stopPropagation")
              v-list-tile-title
                v-icon.drawericon {{ $vuetify.icons.cogs }}
                | Analyze Table
          v-list-tile.small-tile(v-for="a in analyses", :key="a.path",
              :to="{ name: a.shortName }",
              :disabled="!valid(dataset)")
            v-list-tile-title
              v-icon.drawericon {{ $vuetify.icons.compare }}
              | {{a.shortName}}

  keep-alive
    router-view
</template>

<style lang="scss">
.navigation {
  .drawericon {
    vertical-align: top;
    margin-right: 2px;
  }

  // .small-tile .v-list__tile {
  //   height: 32px;
  // }

  // .active {
  //   background-color: #37474f;
  //   border-radius: 40px 0 0 40px;
  //   color: white;
  //   i {
  //     color: white;
  //   }
  // }
  // .file-name .v-list__tile {
  //   padding-right: 0;

  //   .v-list__tile__action {
  //     min-width: 0;
  //     padding-right: 16px;
  //   }
  // }

  // .view-list .v-list__tile--link,
  // .view-list .link-group > .v-list__group__header {
  //   transition: none;

  //   .v-list__tile__title {
  //     transition: none;
  //   }

  //   &:hover {
  //     border-radius: 40px 0 0 40px;
  //   }
  // }
}
</style>
