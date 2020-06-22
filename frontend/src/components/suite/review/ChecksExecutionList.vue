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
    v-expansion-panels(v-if='se.checkExecutions.length > 0')
      v-expansion-panel(v-for='ce in se.checkExecutions' :key='ce.id' elevation=0)
        v-expansion-panel-header

          v-row(no-gutters)
            v-col(cols='12')
              h4.subtitle-1
                v-icon.mr-4(v-if="ce.status === 'Failed'" :color="$store.state.ui.colors.orange" large) mdi-alert
                v-chip.mr-4(v-if='ce.success === true' :color="$store.state.ui.colors.green" text-color="transparent") 0
                v-chip.mr-4(v-if='ce.success === false' :color="$store.state.ui.colors.red" text-color="white") {{ ce.result.payload.length }}
                span {{ ce.title }}

          template(v-slot:actions)
            v-chip.mt-1(
              v-if="ce.inputData.viewId"
              :color="$store.state.ui.colors.orange"
              outlined
              small
              label)
              span {{ ce.inputData.viewId }}

            v-chip.mt-1(
              v-else-if="ce.inputData.webPropertyId"
              :color="$store.state.ui.colors.green"
              outlined
              small
              label)
              span {{ ce.inputData.webPropertyId }}

            v-chip.mt-1(
              v-else-if="ce.inputData.accountId"
              :color="$store.state.ui.colors.blue"
              outlined
              small
              label)
              span {{ ce.inputData.accountId }}

        v-expansion-panel-content
          CheckExecutionDetails(:checkExecution="ce")

    div(v-else)
      span No checks executed.

</template>

<script lang="ts">
  import Vue from 'vue';
  import { SuiteExecution, CheckExecution } from '@/types'
  import CheckExecutionDetails from '@/components/suite/review/CheckExecutionDetails.vue';


  export default Vue.extend({
    components: {
      CheckExecutionDetails
    },

    props: {
      'se': Object as () => SuiteExecution,
    },

    computed: {
      checkExecutions: {
        get(): Array<CheckExecution> { return this.$store.state.business.suite.executions; },
      },
    }

  });
</script>
