<script>
import { sizeFormatter } from '@girder/components/src/utils/mixins';
import Dropzone from '@girder/components/src/components/Presentation/Dropzone.vue';
import FileList from '@girder/components/src/components/Presentation/FileUploadList.vue';
import { UPLOAD_CSV } from '../../store/actions.type';

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
  mixins: [sizeFormatter],
  data() {
    return {
      files:  [],
      message: 'Drop files here or click to upload',
      dataTypes,
      sampleTypes,
    };
  },
  components: {
    FileList,
    Dropzone,
  },
  methods: {
    onFileChange(targetFiles) {
      this.files = [...targetFiles].map(file => ({
        file,
        status: 'pending',
        progress: {},
      }));
    },
    async upload() {
      const promises = this.files.map(async file => {
        file.status = 'uploading';
        try {
          await this.$store.dispatch(UPLOAD_CSV, { file: file.file });
          file.status = 'done';
        } catch (err) {
          file.status = 'error';
          throw err;
        }
      });
      await Promise.all(promises);
      const id = Object.keys(this.$store.state.datasets)[0];
      this.$router.push({ path: `cleanup/${id}` });
    },
  },
};
</script>

<template lang="pug">
v-container(fill-height)
  v-layout(column)
    v-card-title(primary-title)
      div
        h3.headline Upload your data (csv or txt)
        p Choose a file from your computer
    dropzone.filezone(v-if="files.length === 0", :multiple="true",
        :message="message", @change="onFileChange")
    v-layout(row, wrap, shrink)
        v-card.ma-2.filecard(v-for="(file, idx) in files")
          v-card-title(primary-title)
            v-btn(icon, @click="files.splice(idx, 1)")
              v-icon {{ $vuetify.icons.close }}
            div.ml-2
              h3.headline {{ file.file.name }}
              h3 {{ formatSize(file.file.size) }}
          v-card-text
            v-select.pa-2(label="Type of sample",
                :items="sampleTypes", item-text="name", item-value="value")
            v-select.pa-2(label="Type of data",
                :items="dataTypes", item-text="name", item-value="value")
    v-layout.my-4(row)
      v-spacer
      v-btn.ma-0(:disabled="!files.length", large, depressed, color="primary", @click="upload")
        | Continue
        v-icon.pl-1 {{ $vuetify.icons.arrowRight }}
</template>

<style scoped>
.filezone {
  max-height: 200px !important;
}
.filecard {
  min-width: 363px;
}
</style>
