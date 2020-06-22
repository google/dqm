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
    //- Execution button
    v-btn.ml-5(
      @click='runSuite'
      v-if='!isRunning'
      color='primary'
      )
      v-icon(left) mdi-play
      span Execute now

    //- Horiozntal loader if suite is executed in sync mode
    v-container(
      v-else
      height="200")
      v-row.fill-height(align-content='center' justify='center')
        v-col.subtitle-1.text-center(cols='12')
          | Executing your check suite…
        v-col(cols='6')
          v-progress-linear(indeterminate rounded height='6')

</template>

<script lang="ts">
  import Vue from 'vue';

  export default Vue.extend({
    data: () => ({
      isRunning: false,
    }),

    methods: {
      async runSuite() {
        this.isRunning = true;
        await this.$store.dispatch('runSuite');
        // this.suite.executions.push(se);
        // this.suite.checks = se.checks;
        this.isRunning = false;
      },
    },

  });
</script>
