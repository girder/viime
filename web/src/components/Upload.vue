<script>
import { mapState } from 'vuex';
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import Dropzone from '@girder/components/src/components/Presentation/Dropzone.vue';
import FileList from '@girder/components/src/components/Presentation/FileUploadList.vue';
import { UPLOAD_CSV } from '@/store/actions.type';
import { REMOVE_DATASET } from '@/store/mutations.type';

const sampleTypes = [
  { name: 'Serum', value: 'serum' },
  { name: 'Urine', value: 'urine' },
  { name: 'Tissue Extract', value: 'tissueextract' },
  { name: 'Media', value: 'media' },
  { name: 'Other', value: 'other' },
];

const dataTypes = [
  { name: 'NMR Concentrations', value: 'nmr' },
  { name: 'conc', value: 'conc' },
  { name: 'GC/MS', value: 'gcms' },
  { name: 'LC/MS', value: 'lcms' },
  { name: 'Other', value: 'other' },
];

export default {
  components: {
    FileList,
    Dropzone,
  },
  mixins: [sizeFormatter],
  data() {
    return {
      deleteCount: 0,
      doDelete: () => {},
      pendingFiles: [],
      dataTypes,
      sampleTypes,
    };
  },
  computed: {
    ...mapState(['datasets']),
    message() {
      const allFiles = this.pendingFiles.concat(this.readyFiles);
      if (allFiles.length > 0) {
        return 'Add more files';
      }
      return 'Drag file here or click to select one';
    },
    readyFiles() {
      const datasets = this.$store.state.datasets;
      return Object.keys(datasets).map((id) => {
        const d = datasets[id];
        return {
          file: { name: d.source.name, size: 0 },
          status: 'done',
          progress: {},
          meta: d,
        }; 
      });
    },
    files() {
      return this.readyFiles.concat(this.pendingFiles.filter(f => f.status !== 'done'));
    },
    deleteDialog() {
      return this.deleteCount > 0;
    }
  },
  methods: {
    async onFileChange(targetFiles) {
      this.pendingFiles = this.pendingFiles.concat([...targetFiles].map(file => ({
        file,
        status: 'pending',
        progress: {},
        meta: {},
      })));
      const promises = this.pendingFiles
        .filter(f => f.status === 'pending')
        .map(async (file, index) => {
          file.status = 'uploading';
          try {
            await this.$store.dispatch(UPLOAD_CSV,
              { file: file.file, visible: index === 0 });
            file.status = 'done';
          } catch (err) {
            file.status = 'error';
            file.meta = err.response.data;
            throw err;
          }
        });
      await Promise.all(promises);
    },
    async next() {
      const id = Object.keys(this.datasets)[0];
      this.$router.push({ path: `/pretreatment/${id}/cleanup` });
    },
    async remove(file) {
      if (file.status === 'done' && file.meta.source) {
        this.$store.commit(REMOVE_DATASET, { key: file.meta.source.id });
      } else {
        const i = this.pendingFiles.findIndex(f => f.name === file.name && f.size === file.size);
        this.pendingFiles.splice(i, 1);
      }
    },
    removeAll() {
      this.readyFiles.concat(this.pendingFiles).forEach(f => this.remove(f));
    },
  },
};
</script>

<template lang="pug">
v-layout(column, fill-height)

  v-dialog(v-model="deleteDialog", width="600")
    v-card
      v-card-title.headline Really delete {{ deleteCount }} dataset(s)?
      v-card-actions
        v-spacer
        v-btn(@click="doDelete = () => {}; deleteCount = 0;", flat) Cancel
        v-btn(@click="doDelete(); deleteCount = 0", color="error") Delete

  v-layout.overflow-auto(column, fill-height)
    .ma-4
      h3.headline.font-weight-bold.primary--text.text--darken-3 Upload your data (csv or txt)
      p.secondary--text.text--lighten-1 Choose a file from your computer

    .mx-4.mb-4(v-if="files.length")
      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Pending files
        v-spacer
        v-btn(flat, small, @click="deleteCount = files.length; doDelete = removeAll")
          v-icon.pr-1 {{ $vuetify.icons.clearAll }}
          | clear all
      v-list.upload-list
        template(v-for="(file, idx) in files")
          v-list-tile.pa-2(:key="file.file.name + file.status")
            v-list-tile-action
              v-btn(icon, @click="doDelete = () => { remove(file); }; deleteCount = 1;")
                v-icon {{ $vuetify.icons.close }}
            v-list-tile-content.shrink
              v-list-tile-title(v-text="`${file.file.name} `")
              v-list-tile-sub-title(v-text="formatSize(file.file.size)")
            v-list-tile-content.px-2(v-if="file.status === 'error'")
              v-chip(color="error", text-color="white")
                v-icon.pr-1 {{ $vuetify.icons.warning }}
                span(v-if="file.meta.name") {{ file.meta.name[0] }}
                span(v-else) Fatal Error
            v-list-tile-content.px-2(v-else-if="file.status === 'uploading'")
              v-progress-circular(color="primary", indeterminate)
            v-list-tile-content.px-2(v-else-if="file.status === 'done'")
              v-chip(color="success", text-color="white")
                v-icon.pr-1 {{ $vuetify.icons.check }}
                span File processed successfully
            v-spacer
            v-layout(row, shrink)
              v-select.pa-2.tag-selection(hide-details,
                  :disabled="true",
                  :items="sampleTypes", label="Type of sample",
                  item-text="name", item-value="value")
              v-select.pa-2.tag-selection(hide-details,
                  :disabled="true",
                  :items="dataTypes", label="Type of data",
                  item-text="name", item-value="value")
          v-divider(v-if="idx + 1 < files.length", :key="idx")
    dropzone.filezone.mx-4.mb-4(:multiple="true", :message="message", @change="onFileChange")

  v-toolbar(flat, dense)
    v-spacer
    v-btn.ma-0(:disabled="readyFiles.length === 0", depressed, color="accent", @click="next")
      | Continue
      v-icon.pl-1 {{ $vuetify.icons.arrowRight }}
</template>

<style scoped>
.tag-selection {
  width: 200px;
}

.filezone {
  min-width: 300px;
  min-height: 250px;
}
</style>
