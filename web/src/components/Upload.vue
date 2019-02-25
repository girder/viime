<template lang="pug">
.uploader-wrapper
  v-layout(row, wrap, justify-space-between)
    .grow
      v-card-title(primary-title)
        div
          h3.headline Upload your data (csv or txt)
          p Choose a file from your computer
    .grow.ma-3.filezone
      dropzone(:files="files", :multiple="true", :message="message", @change="onFileChange")
      v-card(v-if="files.length > 0")
        file-list(:files="files", @remove="files.splice($event, 1)")
  v-card-actions
    v-spacer
    v-btn(depressed, color="primary", @click="upload") Next Step
</template>

<script>
import Dropzone from '@girder/components/src/components/Presentation/Dropzone.vue';
import FileList from '@girder/components/src/components/Presentation/FileUploadList.vue';
import { UPLOAD_CSV } from '../store/actions.type';

export default {
  data() {
    return {
      files:  [],
      message: 'Upload your file',
    };
  },
  components: {
    FileList,
    Dropzone,
  },
  methods: {
    onFileChange({ target }) {
      this.files = [...target.files].map(file => ({
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
      this.$router.push({ path: 'transform'});
    },
  },
};
</script>

<style scoped>
.filezone {
  min-height: 200px !important;
  min-width: 300px !important;
}
</style>
