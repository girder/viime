<template lang="pug">
v-layout(row)
  div(v-for="table in sourcedata")
    p(v-for="col in table.columns") {{ col.name }}
</template>

<script>
import { mapState } from 'vuex';

export default {
  computed: mapState(['sourcedata']),
}
</script>

<style>

</style>
