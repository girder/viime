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
    problemNav(problem) {
      if (problem.multi) {
        this.$router.push({ name: 'Problem', params: { problem: problem.type } });
      } else {
        this.$router.push({ name: 'Clean Up Table' });
        this.$store.commit(SET_SELECTION, {
          key: this.id,
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

  v-navigation-drawer.navigation(floating, permanent, style="min-width: 220px; width: 220px;")
    v-list
      v-list-group.root-level(v-for="(dataset, index) in datasets",
          :key="dataset.id",
          :class="{ active: $route.name === 'Pretreat Data' && dataset.id === id}",
          :value="dataset.id === id")
        template(#activator)
          v-list-tile.dataset-level(:to="{ name: 'Pretreat Data', params: { id: dataset.id } }",
              exact, @click="stopPropagation")
            v-list-tile-title.title
              | {{ dataset.name }}
            v-list-tile-action
              v-icon(color="warning", v-if="dataset.validation.length")
                | {{ $vuetify.icons.warning }}
              v-icon(color="success", v-else)
                | {{ $vuetify.icons.check }}

        v-list-tile.top-level(:to="{ name: 'Clean Up Table' }", exact)
          v-list-tile-title
            v-icon.drawericon {{ $vuetify.icons.tableEdit }}
            | Clean Up Table

        v-list-tile.sub-level(v-for="problemData in dataset.validation",
            @click="problemNav(problemData)",
            :class="{ active: problemData.type === problem && dataset.id === id}",
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

        v-list-tile.sub-level(:to="{ name: 'Impute Table' }")
          v-list-tile-title
            v-icon.drawericon {{ $vuetify.icons.tableEdit }}
            | Impute Table

        v-list-tile.top-level(:to="{ name: 'Transform Table' }",
            :disabled="!valid(dataset)")
          v-list-tile-title
            v-icon.pr-1.drawericon {{ $vuetify.icons.bubbles }}
            | Transform Table

        v-list-group.top-level(sub-group,
            :class="{ active: $route.name === 'Analyze Data' && dataset.id === id}",
            value="true")
          template(#activator)
            v-list-tile.top-level(:to="{ name: 'Analyze Data' }", exact,
                :disabled="!valid(dataset)",
                @click="stopPropagation")
              v-list-tile-title
                v-icon.drawericon {{ $vuetify.icons.cogs }}
                | Analyze Table
          v-list-tile.sub-level(v-for="a in analyses", :key="a.path",
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
  > .v-list {
    padding: 0;

    > .v-list__group > .v-list__group__items {
      padding: 8px 0;
    }
  }

  .drawericon {
    vertical-align: top;
    margin-right: 4px;
  }

  .root-level > .v-list__group__header--active {
    background: unset;
  }

  .root-level.active > .v-list__group__header {
    background-color: #37474f;
  }

  .root-level.active > .v-list__group__header,
  .top-level.active > .v-list__group__header {
    .v-list__group__header__prepend-icon > .v-icon,
    .v-list__group__header__append-icon > .v-icon,
    .v-list__tile__title {
      color: white !important;
    }
  }

  .dataset-level {
    order: 2;

    .v-list__tile {
      padding: 0 8px 0 0;
      color: black !important;

      &:hover {
        background: unset;
      }
    }

    .v-list__tile__action {
      min-width: unset;
    }
  }

  .top-level {
    .v-list__group__header {
      position: relative;

      &:hover {
        background: unset;
      }

      .v-list__tile {
        padding-left: 16px;

      }
    }

    .v-list__group__header__prepend-icon {
      min-width: unset;
      padding: 0;
      margin: 0;
      justify-content: flex-end;
      z-index: 1;
      position: absolute;
      left: 8px;
      top: 0;
      height: 100%;
    }

    // .v-list__group__header--active > .v-list__group__header__prepend-icon > .v-icon {
    //   color: white;
    // }
  }


  .sub-level {
    margin: 4px 0 4px 24px;

    .v-list__tile {
      height: 32px;
    }
  }

  > .v-list {
    .top-level {
      > .v-list__tile {
        margin-left: 8px;

        .v-list__tile__title  {
          padding-left: 8px;
        }
      }
    }

    .sub-level {
      > .v-list__tile {
        margin-left: 8px;

        .v-list__tile__title  {
          padding-left: 4px;
        }
      }
    }

    .top-level,
    .sub-level {
      > .v-list__tile {
        border-radius: 24px 0 0 24px;

        .v-list__tile__title  {
          font-size: 16px;
        }
      }

      > .v-list__tile--active {
        background-color: #37474f;
        color: white;

        &:hover {
          background-color: #4b616d;
        }

        i,
        .v-list__tile__title {
          color: white;
        }
      }
    }

    // .group-level {
    //   > .v-list__tile {

    //     .v-list__tile__title {
    //       font-size: 16px;
    //     }

    //     &:hover {
    //       background: unset;
    //     }
    //   }

    //   > .v-list__tile--active {
    //     color: white;

    //     i,
    //     .v-list__tile__title {
    //       color: white;
    //     }
    //   }
    // }
  }
}
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
</style>
