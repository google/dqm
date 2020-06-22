<!--
 Copyright 2020 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<template lang="pug">
  v-app-bar(app clipped-left fixed dark flat color='blue darken-2')
    v-app-bar-nav-icon(@click="$store.commit('sidebar')")
    v-toolbar-title(@click="$router.push({name: 'home'})") Data Quality Manager
    v-spacer
    v-btn(
      text
      @click="showSuiteCreationDialog = true")
      | New suite

    SuiteCreation(
      :show="showSuiteCreationDialog"
      @updateShowSuiteCreationDialog="showSuiteCreationDialog = false")

</template>

<script lang="ts">
  import Vue from 'vue';
  import SuiteCreation from '@/components/SuiteCreation.vue';

  export default Vue.extend({
    components: {
      SuiteCreation
    },

    data: () => ({
      showSuiteCreationDialog: false
    }),

  });
</script>
