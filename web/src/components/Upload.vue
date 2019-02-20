<template lang="pug">
  v-card.pa-2(flat)
    v-card-title(primary-title)
      v-layout(row, align-start)
        v-radio.py-2(value="true")
        div
          h3.headline Upload your data (csv or txt)
          p Choose a file from your computer
    v-card-text
      input(type="file", name="file", id="file", ref="file", @change="onFileChange")
      v-btn(@click="upload") Upload
    v-divider.my-4
    v-card-title(primary-title)
      div
        h3.headline Don't have your own data?
        p Choose from the following sample data.
    v-card-text
      v-layout(row, justify-space-between)
        v-card
          v-card-title Dataset 1
          v-card-text Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        v-card
          v-card-title Dataset 2
          v-card-text Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        v-card
          v-card-title Dataset 3
          v-card-text Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
    v-divider.my-4
    v-layout(row)
      v-btn(depressed, color="secondary") Previous Step
      v-spacer
      v-btn(depressed, color="secondary") Next Step
</template>

<script>
import { CSVService } from '../common/api.service.js';

export default {
  data() {
    return {
      radios: null,
      file:  null,
    };
  },
  methods: {
    onFileChange() {
      this.file = this.$refs.file.files[0];
    },
    async upload() {
      const formData = new FormData();
      formData.append('file', this.file);
      const { data } = await CSVService.upload(formData);
    },
  },
};
</script>

<style>

</style>
