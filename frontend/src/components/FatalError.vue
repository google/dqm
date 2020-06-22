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
    v-main
      v-container(fluid)
        v-alert(type="error")
          p Oops, DQM encountered a fatal error and can't load. Please reload the page or contact you DQM admin.
          code {{ $store.state.ui.fatalError.text }}

        v-card(outlined)
          v-container(fluid)
            pre {{ $store.state.ui.fatalError.details }}

</template>

<script lang="ts">
  import Vue from 'vue';

  export default Vue.extend({
  });
</script>