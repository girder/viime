<script>
import BrowserSupportBanner from './BrowserSupportBanner.vue';
import HighlightImage from './HighlightImage.vue';
import FeedbackButton from './FeedbackButton.vue';
import analysis_05x from '../assets/capabilities/analysis_05x.png';
import analysis from '../assets/capabilities/analysis_1x.png';
import analysis_2x from '../assets/capabilities/analysis_2x.png';
import feedback_05x from '../assets/capabilities/feedback_05x.png';
import feedback from '../assets/capabilities/feedback_1x.png';
import feedback_2x from '../assets/capabilities/feedback_2x.png';
import ingestion_05x from '../assets/capabilities/ingestion_05x.png';
import ingestion from '../assets/capabilities/ingestion_1x.png';
import ingestion_2x from '../assets/capabilities/ingestion_2x.png';
import integration_05x from '../assets/capabilities/integration_05x.png';
import integration from '../assets/capabilities/integration_1x.png';
import integration_2x from '../assets/capabilities/integration_2x.png';
import visualization_05x from '../assets/capabilities/visualization_05x.png';
import visualization from '../assets/capabilities/visualization_1x.png';
import visualization_2x from '../assets/capabilities/visualization_2x.png';

export default {
  components: {
    BrowserSupportBanner,
    HighlightImage,
    FeedbackButton,
  },
  data() {
    return {
      capabilityClasses: {
        'px-4': this.$vuetify.breakpoint.smAndDown,
        'px-0': this.$vuetify.breakpoint.mdAndUp,
      },
      showViimePath: JSON.parse(localStorage.getItem('showViimePath') ?? 'true'),
      diclaimerOpen: false,
      images: {
        analysis,
        feedback,
        ingestion,
        integration,
        visualization,
      },
      srcset: {
        analysis: `${analysis} 1x, ${analysis_05x} 0.5x, ${analysis_2x} 2x`,
        feedback: `${feedback} 1x, ${feedback_05x} 0.5x, ${feedback_2x} 2x`,
        ingestion: `${ingestion} 1x, ${ingestion_05x} 0.5x, ${ingestion_2x} 2x`,
        integration: `${integration} 1x, ${integration_05x} 0.5x, ${integration_2x} 2x`,
        visualization: `${visualization} 1x, ${visualization_05x} 0.5x, ${visualization_2x} 2x`,
      },
    };
  },
  methods: {
    hideViimePath() {
      localStorage.setItem('showViimePath', 'false');
      this.showViimePath = false;
    },
  },
};
</script>
<template lang="pug">
v-app.viime-landing
  div(v-if="showViimePath", style="position:absolute;top:70px;left:20px;z-index:100")
    v-card.mx-auto
      v-card-text
        div(style="display:flex;flex-direction:row;justify-content:flex-start")
          div(style="max-width:700px")
            p(style="font-size:30px")
              | See the new module &nbsp;
              a(href="https://girder.github.io/viime-path/") Viime-Path
            div(style="font-size:20px")
              | Viime-Path: An Interactive Metabolic Pathway
              | Generation Tool for Metabolomics Data Analysis
              br
              | Jeff Baumes, Thomas M. O'Connell
              br
              | doi:&nbsp;
              a(href="https://doi.org/10.1101/2023.03.07.531550")
                | https://doi.org/10.1101/2023.03.07.531550
          v-btn(icon, @click="hideViimePath")
            v-icon mdi-close

  browser-support-banner
  v-toolbar.main-toolbar.darken-4.py-2(dark, dense, color="transparent", flat)
    v-toolbar-title(style="height: 100%; padding: 10px 0;")
      img(src="../assets/viime_logo_ko.svg", alt="VIIME", height="100%")
    v-spacer
    v-btn(color="accent", depressed, large, :to="{ name: 'App' }") Your Datasets

  v-container.banner-area(fluid, pa-0)
    v-layout(row, reverse)
      v-flex(md5, pa-0)
        v-card.banner-image(color="white", flat)
          highlight-image.img
      v-flex.banner-content-wrap.primary.darken-4(md7)
        v-card.banner-content(color="transparent", dark, flat)
          highlight-image.img(small)
          v-card-title.banner-title.px-0
            h1 Combine your metabolomics data. Interact with the results.
          v-card-text.banner-text.px-0
            p.primary--text.text--lighten-2
              span.white--text VIIME (VIsualization and Integration of Metabolomics Experiments)
              |  provides a new workflow for metabolomics research by offering state-of-the-art
              | integration algorithms and visualizations.
          v-card-actions.banner-buttons.px-0
            v-btn(color="accent", depressed, large, :to="{ name: 'Try Data' }") Try it now
      .scroll-down
        .scroll-down-wrap
          span
          span
          span
          span
        | scroll to
        br
        | learn more
  .capabilities
    v-container(fluid, pa-0)
      v-layout.capability
        v-container(:class="capabilityClasses", py-2x)
          v-layout(align-center, pa-0, row, wrap)
            v-flex.capability-col(px-3, py-2, sm4)
              v-card(color="transparent", flat, pa-0)
                v-img.elevation-3(:src="images.ingestion", :aspect-ratio="750 / 450",
                    :srcset="srcset.ingestion")
            v-flex.capability-col(px-3, py-2, sm8)
              v-card(color="transparent", flat)
                v-card-title.capability-title.py-0(primary-title)
                  h1.primary--text.text--darken-3 Flexible data ingestion
                v-card-text.capability-text
                  | Upload csv or Excel files and work through a semi-automated process which alerts
                  |  you to low-variance and high-missingness data, allows arbitrary sample and
                  |  metabolite exclusion, and performs adjustable missing data imputation

      v-layout.capability
        v-container(:class="capabilityClasses", py-5)
          v-layout(align-center, pa-0, row, wrap)
            v-flex.capability-col(px-3, py-2, sm4)
              v-card(color="transparent", flat, pa-0)
                v-img.elevation-3(:src="images.feedback", :aspect-ratio="750 / 650",
                    :srcset="srcset.feedback")
            v-flex.capability-col(px-3, py-2, sm8)
              v-card(color="transparent", flat)
                v-card-title.capability-title.py-0(primary-title)
                  h1.primary--text.text--darken-3 Immediate visual feedback
                v-card-text.capability-text
                  | See how ingestion, pretreatment, and analysis options affect results live as you
                  |  make adjustments

      v-layout.capability
        v-container(:class="capabilityClasses", py-5)
          v-layout(align-center, pa-0, row, wrap)
            v-flex.capability-col(px-3, py-2, sm4)
              v-card(color="transparent", flat, pa-0)
                v-img.elevation-3(:src="images.integration", :aspect-ratio="750 / 450",
                    :srcset="srcset.integration")
            v-flex.capability-col(px-3, py-2, sm8)
              v-card(color="transparent", flat)
                v-card-title.capability-title.py-0(primary-title)
                  h1.primary--text.text--darken-3 Modern integration methods
                v-card-text.capability-text
                  | Run algorithms like PCA and Block PCA to obtain more accurate results using data
                  |  from multiple measurement platforms (NMR, MS) or tissues (serum, urine, etc.)

      v-layout.capability
        v-container(:class="capabilityClasses", py-5)
          v-layout(align-center, pa-0, row, wrap)
            v-flex.capability-col(px-3, py-2, sm4)
              v-card(color="transparent", flat, pa-0)
                v-img.elevation-3(:src="images.analysis", :aspect-ratio="750 / 450",
                    :srcset="srcset.analysis")
            v-flex.capability-col(px-3, py-2, sm8)
              v-card(color="transparent", flat)
                v-card-title.capability-title.py-0(primary-title)
                  h1.primary--text.text--darken-3 Relevant Analyses
                v-card-text.capability-text
                  | Run algorithms like Wilcoxon and ANOVA to highlight metabolites for further
                  |  investigation, and export resulting data and charts

      v-layout.capability
        v-container(:class="capabilityClasses", py-5)
          v-layout(align-center, pa-0, row, wrap)
            v-flex.capability-col(px-3, py-2, sm4)
              v-card(color="transparent", flat, pa-0)
                v-img.elevation-3(:src="images.visualization", :aspect-ratio="750 / 450",
                    :srcset="srcset.visualization")
            v-flex.capability-col(px-3, py-2, sm8)
              v-card(color="transparent", flat)
                v-card-title.capability-title.py-0(primary-title)
                  h1.primary--text.text--darken-3 Advanced visualizations
                v-card-text.capability-text
                  | Make use of interactive tables, charts, heatmaps, and network diagrams to get
                  |  the best understanding of your experimental data
  .partners
    v-container(py-5)
      v-layout(row, wrap)
        v-flex.partner(sm4)
          v-card.pa-3(color="transparent", flat)
            v-card-title.partner-title.pt-3(primary-title)
              img.mr-1(alt="Kitware, Inc.", src="../assets/kw_logo_mark.jpg", height="auto")
              h2 Kitware, Inc.
            v-card-text.pa-0
              v-list.team-members
                v-list-tile(href="https://www.kitware.com/data-analytics/",
                    target="_blank", rel="noopener noreferrer")
                  v-list-tile-content
                    v-list-tile-title Data and Analytics team
                  v-list-tile-action
                    v-icon(color="accent lighten-1") $vuetify.icons.openInNew
        v-flex.partner(sm4)
          v-card.pa-3(color="transparent", flat)
            v-card-title.partner-title.pt-3(primary-title)
              img.mr-1(alt="Indiana University", src="../assets/iu_logo_mark.jpg", height="auto")
              h2 Indiana University
            v-card-text.pa-0
              v-list.team-members
                v-list-tile(href="https://medicine.iu.edu/research/faculty-labs/oconnell/",
                    target="_blank", rel="noopener noreferrer")
                  v-list-tile-content
                    v-list-tile-title Thomas O'Connell
                  v-list-tile-action
                    v-icon(color="accent lighten-1") $vuetify.icons.openInNew
                v-divider
                v-list-tile
                  v-list-tile-content
                    v-list-tile-title Jun Wang
                v-divider
                v-list-tile
                  v-list-tile-content
                    v-list-tile-title Lilian Golzarri-Arroyo
        v-flex.partner(sm4)
          v-card.pa-3(color="transparent", flat)
            v-card-title.partner-title.pt-3(primary-title)
              img.mr-2(alt="University of Washington", src="../assets/uw_logo_mark.jpg",
                  height="auto")
              h2 University of Washington
            v-card-text.pa-0
              v-list.team-members
                v-list-tile(href="https://sites.uw.edu/mmcslu/faculty/daniel-raftery-phd/",
                    target="_blank", rel="noopener noreferrer")
                  v-list-tile-content
                    v-list-tile-title Daniel Raftery
                  v-list-tile-action
                    v-icon(color="accent lighten-1") $vuetify.icons.openInNew

  .collaboration
    v-container
      v-layout(row, wrap)
        v-flex(md8, xs12)
          h2.mb-3.pa-0 Ready for Collaboration
          p
            | The code for Viime is in a permissive open source library, meaning it can be used and
            | extended across academia and industry with no restrictions. This includes deploying
            | Viime at your institution for your internal research team. If you'd like to partner
            | with us to deploy or extend Viime
        v-flex.contacts(md4, xs12)
          div
            feedback-button(front)
            v-btn(href="https://github.com/girder/viime", depressed, large,
                target="_blank", rel="noopener noreferrer")
              v-icon.mr-2(left) $vuetify.icons.github
              | View on GitHub

  .footer
    p.ma-0.pa-3
      | &copy; 2019 Kitware, Inc. |&nbsp;

      a(href="https://github.com/girder/viime/blob/master/LICENSE",
          target="_blank", rel="noopener noreferrer") Apache License 2.0

      | &nbsp;|&nbsp;

      a(href="https://www.kitware.com/privacy",
          target="_blank", rel="noopener noreferrer") Privacy Notice

      | &nbsp;|&nbsp;

      v-dialog(v-model="diclaimerOpen", max-width="33vw")
        template(#activator="{ on }")
          a(v-on="on", href="#/") Disclaimer
        v-card
          v-card-title
            h3.headline Diclaimer
          v-card-text
            | This is beta software.
            | As such, please use at your own risk and validate any analysis result
            | externally before publication.
            | For research purposes only. Due to current technical limitations,
            | data may be stored on our servers
            | even after data is deleted from the client application.
          v-card-actions
            v-spacer
            v-btn(@click="diclaimerOpen = false") Ok
</template>

 <style lang="scss" scoped>
.viime-landing {
  background: white;
}
.main-toolbar {
  position: relative;
  z-index: 2;
}

.banner-area {
  box-sizing: border-box;
  height: 100vh;
  margin-top: -64px;
  position: relative;
  z-index: 1;
  & > .layout {
    height: 100%;
  }
  .banner-content-wrap {
    padding: 0;
  }
  .banner-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: center;
    padding: 0 145px 0 60px;
    .img {
      display: none;
    }
    .layout > * {
      width: 100%;
    }
    .banner-title {
      h1 {
        font-size: 72px;
        font-weight: normal;
        line-height: 1em;
      }
    }
    .banner-text {
      font-size: 26px;
    }
    .banner-buttons {
      button {
        font-size: 24px;
        height: auto;
        padding-bottom: 10px;
        padding-top: 10px;
      }
    }
  }
  .banner-image {
    height: 100%;
    position: relative;
    width: 100%;

    .img {
      position: absolute;
      left: -130px;
      top: 50%;
      transform: translatey(-50%);
      max-height: 100%;
      max-width: 98%;
    }
  }
}

.capabilities {
  background: #f5f5f5;
  .capability {
    &:nth-of-type(odd) {
      .layout {
        flex-direction: row-reverse;
      }
    }
    .capability-title {
      font-size: 18px;
    }
    .capability-text {
      font-size: 25px;
    }
  }
}
.partners {
  .partner {
    .team-members {
      border-top:4px solid var(--v-accent-lighten1);
      border-radius: 3px;
      padding: 0;
    }
    .partner-title {
      line-height: 48px;
      white-space: nowrap;
      flex-wrap: nowrap;

      img {
        width: 48px;
        min-width: 32px;
      }
    }
  }
}
.scroll-down {
  align-items: flex-end;
  bottom: 50px;
  color: var(--v-primary-lighten2);
  display: inline-flex;
  font-size: 18px;
  left: 75px;
  line-height: 1.1em;
  position: absolute;
  .scroll-down-wrap {
    height: 48px;
    width: 15px;
    span {
      animation: animate 2.2s infinite;
      border-bottom: 2px solid var(--v-primary-lighten2);
      border-right: 2px solid var(--v-primary-lighten2);
      display: block;
      height: 10px;
      margin: -10px;
      transform: rotate(45deg);
      width: 10px;
    }

    span:nth-child(2) {
      animation-delay: -0.2s;
    }

    span:nth-child(3) {
      animation-delay: -0.4s;
    }

    span:nth-child(4) {
      animation-delay: -0.6s;
    }
  }
}

.collaboration {
  background-color: var(--v-primary-darken4);
  color: #fff;
  font-size: 18px;
  padding: 15px 20px 30px;
  position: relative;
  &:before {
    border-color: #ffffff transparent transparent transparent;
    border-style: solid;
    border-width: 15px 20px 0 20px;
    content: '';
    height: 0;
    left: 50%;
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    width: 0;
  }
}

.contacts {
  display: flex;
  flex-direction: row;
  justify-content: center;

  > div {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
  }
}

.footer {
  text-align: center;

  a {
    color: rgba(0,0,0,0.87);
  }
}

@keyframes animate {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 0.5;
    transform: rotate(45deg) translate(30px, 30px);
  }
  80% {
    opacity: 1;
    transform: rotate(45deg) translate(30px, 30px);
  }
  100% {
    opacity: 0;
    transform: rotate(45deg) translate(30px, 30px);
  }
}

@media screen and (max-width: 960px) {
  .banner-area {
    height: auto;
    .banner-content-wrap {
      min-height: 860px;
    }
    .banner-content {
      padding: 0 45px;
      text-align: center !important;
      .img {
        display: block;
      }
      .banner-title {
        h1 {
          font-size: 36px;
          margin: 0 auto;
        }
      }
      .banner-text {
        font-size: 18px;
      }
      .banner-buttons {
        margin: 0 auto;
      }
    }
    .banner-image {
      display: none;
    }
  }
  .capabilities {
    .capability {
      .capability-title {
        font-size: 14px;
      }
      .capability-text {
        font-size: 14px;
      }
    }
  }
}
</style>

<style lang="scss">
.viime-landing {
  .application--wrap {
    display: block;
    min-height: 100%;
  }
}
</style>
