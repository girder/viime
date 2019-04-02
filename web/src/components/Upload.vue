<script>
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import Dropzone from '@girder/components/src/components/Presentation/Dropzone.vue';
import FileList from '@girder/components/src/components/Presentation/FileUploadList.vue';
import { UPLOAD_CSV } from '@/store/actions.type';

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
      files: [],
      dataTypes,
      sampleTypes,
    };
  },
  computed: {
    message() {
      if (this.files.length) {
        return 'Add more files';
      }
      return 'Drag file here or click to select one';
    },
  },
  methods: {
    onFileChange(targetFiles) {
      this.files = this.files.concat([...targetFiles].map(file => ({
        file,
        status: 'pending',
        progress: {},
      })));
    },
    async upload() {
      const promises = this.files.map(async (file, index) => {
        file.status = 'uploading';
        try {
          await this.$store.dispatch(UPLOAD_CSV,
            { file: file.file, visible: index === 0 });
          file.status = 'done';
        } catch (err) {
          file.status = 'error';
          throw err;
        }
      });
      await Promise.all(promises);
      const id = Object.keys(this.$store.state.datasets)[0];
      this.$router.push({ path: `/pretreatment/${id}/cleanup` });
    },
  },
};
</script>

<template lang="pug">
v-layout(column, fill-height)
  v-layout.overflow-auto(column, fill-height)
    v-card-title.pa-4(primary-title)
      div
        h3.headline.font-weight-bold.primary--text.text--darken-3 Upload your data (csv or txt)
        p.secondary--text.text--lighten-1 Choose a file from your computer

    .mb-0.mx-4(v-if="files.length")
      v-toolbar.darken-3(color="primary", dark, flat, dense)
        v-toolbar-title Pending files
        v-spacer
        v-btn(flat, small, @click="files = []")
          v-icon.pr-1 {{ $vuetify.icons.clearAll }}
          | clear all
      v-list.upload-list
        template(v-for="(file, idx) in files")
          v-list-tile.pa-2(:key="file.file.name")
            v-list-tile-action
              v-btn(icon, @click="files.splice(idx, 1)")
                v-icon {{ $vuetify.icons.close }}
            v-list-tile-content
              v-list-tile-title(v-text="file.file.name")
              v-list-tile-sub-title(v-text="formatSize(file.file.size)")
            v-spacer
            v-layout(row, shrink)
              v-select.pa-2.tag-selection(hide-details,
                  :items="sampleTypes", label="Type of sample",
                  item-text="name", item-value="value")
              v-select.pa-2.tag-selection(hide-details,
                  :items="dataTypes", label="Type of data",
                  item-text="name", item-value="value")
          v-divider(v-if="idx + 1 < files.length", :key="idx")
    dropzone.filezone.mx-4.my-2(:multiple="true", :message="message", @change="onFileChange")

  v-toolbar(flat, dense)
    v-spacer
    v-btn.ma-0(:disabled="!files.length", depressed, color="accent", @click="upload")
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