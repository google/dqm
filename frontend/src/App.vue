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

  v-app(id="inspire")
    FatalError(v-if="$store.state.ui.fatalError")

    template(v-else)
      Menu
      AppBar

      v-main
        v-container(fluid)
          router-view(:key="$route.fullPath")

      Footer

      v-snackbar(v-model='$store.state.ui.snackbar.show')
        span {{ $store.state.ui.snackbar.text }}
        template(v-slot:action="{ attrs }")
          v-btn(text @click='$store.state.ui.snackbar.show = false') Close

</template>

<script lang="ts">
  import Vue from 'vue';
  import AppBar from '@/components/AppBar.vue';
  import Menu from '@/components/Menu.vue';
  import Footer from '@/components/Footer.vue';
  import FatalError from '@/components/FatalError.vue';

  export default Vue.extend({
    name: 'App',

    components: {
      AppBar,
      Menu,
      Footer,
      FatalError
    },

    created() {
      this.$store.dispatch('fetchCache');
      this.$store.dispatch('fetchChecksMetadata');
      this.$store.dispatch('fetchAppSettings');
      this.$store.dispatch('fetchGaAccounts');

      //TODO: fix this properly
      document.title = window.location.hostname.split('.')[0];
    },

    watch: {
      '$route' (to) {
        document.title = to.meta.title || window.location.hostname.split('.')[0];
      }
    },

  });
</script>


<style>
  #inspire {
    background-color: #fafafa;
  }
</style>