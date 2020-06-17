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
    id: {
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
    isMerged(dataset) {
      return this.$store.getters.isMerged(dataset.id);
    },
    problemNav(problem, id) {
      if (problem.multi) {
        this.$router.push({ name: 'Problem', params: { id, problem: problem.type } }).catch(() => {});
      } else {
        this.$router.push({ name: 'Clean Up Table', params: { id } }).catch(() => {});
        this.$store.commit(SET_SELECTION, {
          key: id,
          event: {},
          axis: problem.context,
          idx: problem[`${problem.context}_index`],
        });
      }
    },
  },
};
</script>

<template lang="pug">
v-layout.pretreatment-component(row, fill-height)

  v-navigation-drawer.navigation(floating, permanent, style="min-width: 220px; width: 220px;",
      touchless, disable-resize-watcher, stateless)
    v-list(dense)
      v-list-group(
          v-for="(dataset, index) in datasets",
          :key="dataset.id",
          :class="{ active: $route.name === 'Pretreat Data' && dataset.id === id}",
          :value="dataset.id === id")
        template(#activator)
          v-list-tile.mr-0.pr-2(
              @click.stop="",
              active-class="font-weight-bold",
              :to="{ name: 'Pretreat Data', params: { id: dataset.id } }",
              exact)
            v-list-tile-title.grow
              | {{ dataset.name }}
            v-list-tile-action.action-style
              v-icon(color="warning", v-if="dataset.validation.length")
                | {{ $vuetify.icons.warning }}
              v-icon(color="success", v-else)
                | {{ $vuetify.icons.check }}

        v-list-tile(
            :to="{ name: 'Clean Up Table', params: { id: dataset.id } }",
            exact,
            active-class="font-weight-bold")
          v-list-tile-action.action-style
            v-icon {{ $vuetify.icons.tableEdit }}
          v-list-tile-content
            v-list-tile-title
              | Clean Up Table

        v-list-tile(
            v-for="problemData in dataset.validation",
            @click="problemNav(problemData, dataset.id)",
            :class="{ active: problemData.type === problem && dataset.id === id}",
            :inactive="!problemData.clickable",
            :key="problemData.title",
            active-class="font-weight-bold")
          v-list-tile-action.action-style
            v-icon.pr-1(
                :color="problemData.severity") {{ $vuetify.icons[problemData.severity] }}
          v-list-tile-content
            v-list-tile-title {{ problemData.title }}
              span(v-if="problemData.data") ({{ problemData.data.length }})
              v-tooltip(v-else, top)
                template(#activator="{ on }")
                  v-icon.pr-1(small, v-on="on") {{ $vuetify.icons.info }}
                span {{ problemData.description }}

        v-list-tile(
            :to="{ name: 'Impute Table', params: { id: dataset.id } }",
            v-show="!isMerged(dataset)",
            active-class="font-weight-bold")
          v-list-tile-action.action-style
            v-icon.pr-1 {{ $vuetify.icons.tableEdit }}
          v-list-tile-content
            v-list-tile-title
              | Impute Table

        v-list-tile(
            :to="{ name: 'Transform Table', params: { id: dataset.id } }",
            :disabled="!valid(dataset)", v-show="!isMerged(dataset)",
            active-class="font-weight-bold")
          v-list-tile-action.action-style
            v-icon.pr-1 {{ $vuetify.icons.bubbles }}
          v-list-tile-content
            v-list-tile-title
              | Transform Table

        v-list.py-0
          v-list-group(
              :class="{ active: $route.name === 'Analyze Data' && dataset.id === id}")
            template(#activator)
              v-list-tile(
                  :to="{ name: 'Analyze Data', params: { id: dataset.id } }",
                  :disabled="!valid(dataset)",
                  exact,
                  active-class="font-weight-bold")
                v-list-tile-action.action-style
                  v-icon.pr-1 {{ $vuetify.icons.cogs }}
                v-list-tile-content
                  v-list-tile-title
                    | Analyze Table
            v-list-tile(
                v-for="a in analyses",
                :key="a.path",
                :to="{ name: a.shortName, params: { id: dataset.id } }",
                :disabled="!valid(dataset)",
                active-class="font-weight-bold")
              v-list-tile-action.action-style
                v-icon.pr-1(:style="a.iconStyle") {{ a.icon || $vuetify.icons.compare }}
              v-list-tile-content
                v-list-tile-title
                  | {{a.shortName}}

        v-list-tile(
            :to="{ name: 'Download Data', params: { id: dataset.id } }",
            :disabled="!valid(dataset)",
            active-class="font-weight-bold")
          v-list-tile-action.action-style
            v-icon.pr-1 {{ $vuetify.icons.fileDownload }}
          v-list-tile-content
            v-list-tile-title
              | Download Data

  router-view
</template>

<style scoped>
.action-style {
  min-width: 40px !important;
}
</style>
