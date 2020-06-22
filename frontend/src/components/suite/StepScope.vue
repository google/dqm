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
  div
    template
      v-card(flat outlined)

        v-tabs(v-model="tab")
          v-tab Google Analytics
          v-tab(disabled) Google Ads
          v-tab(disabled) DV360
          v-tab(disabled) SA360

          v-tab-item(transition="false" reverse-transition="false")
            ScopeGa

</template>

<script lang="ts">
  import Vue from 'vue';
  import ScopeGa from '@/components/suite/scope/ScopeGa.vue';

  export default Vue.extend({
    components: {
      ScopeGa
    },

    data: () => ({
      tab: 0,
    }),

  });
</script>

