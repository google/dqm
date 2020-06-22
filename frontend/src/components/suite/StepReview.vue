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
      v-row(justify='space-between')
        v-col
          ReviewActions
          ReviewExecutions

</template>

<script lang="ts">
  import Vue from 'vue';
  import ReviewActions from '@/components/suite/review/ReviewActions.vue';
  import ReviewExecutions from '@/components/suite/review/ReviewExecutions.vue';

  export default Vue.extend({
    components: {
      ReviewActions,
      ReviewExecutions
    },

    props: {
      'checks': Array,
      'executions': Array,
      'isRunning': Boolean,
    },

    data: () => ({
      dialog: true,

      running: false,
      expanded: [],

      // checksModel: [],

      executionsTable: {
        search: '',
        loading: true,
        headers: [
          {text: 'Result', value: 'success'},
          {text: 'Execution date', value: 'executed'},
          {text: 'Checks executed', value: 'checksCount'},
          { text: '', value: 'data-table-expand' },
        ],
        data: [],
      },
    }),


    watch: {
      executions: {
        immediate: true,
        handler(value) {
          this.executionsTable.data = value;
        },
      },

      isRunning: {
        immediate: true,
        handler(value) {
          this.running = value;
        },
      },

    },

  });
</script>
