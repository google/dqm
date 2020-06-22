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
    //- Previous execution summary/details
    div.mt-8(v-if='executions.length > 0')
      v-data-table.elevation-1(
        :headers="executionsDataTable.headers"
        :items="executions"
        :items-per-page='20'
        sort-by='executed'
        sort-desc
        show-expand
        single-expand
        :expanded.sync="expanded")

        template(v-slot:expanded-item='{ headers, item }')
          td(:colspan='executionsDataTable.headers.length').pa-4
            ChecksExecutionList(:se="item")

        template(v-slot:item.executed='{ item }')
          span {{ item.executed | formatDate }}

        template(v-slot:item.success='{ item }')
          //- v-progress-circular(v-if='item.success === null' indeterminate :size='20' :width='2' color='grey lighten-1')
          v-icon(v-if='item.success === true' :color="$store.state.ui.colors.green") mdi-circle
          v-icon(v-if='item.success === false' :color="$store.state.ui.colors.red") mdi-circle
          v-icon(v-if='item.success === null' :color="$store.state.ui.colors.red") mdi-circle

        template(v-slot:item.checksCount='{ item }')
          span(@click='dialog=true') {{ item.checkExecutions.length }}
</template>

<script lang="ts">
  import Vue from 'vue';
  import { SuiteExecution } from '@/types';
  import ChecksExecutionList from '@/components/suite/review/ChecksExecutionList.vue';

  export default Vue.extend({
    components: {
      ChecksExecutionList
    },

    data: () => ({
      expanded: [],
      executionsDataTable: {
        search: '',
        loading: true,
        headers: [
          {text: 'Result', value: 'success'},
          {text: 'Execution date', value: 'executed'},
          {text: 'Checks executed', value: 'checksCount'},
          { text: '', value: 'data-table-expand' },
        ],
      },
    }),

    computed: {
      executions(): Array<SuiteExecution> { return this.$store.state.business.suite.executions; },
    },

  });
</script>
