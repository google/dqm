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
    div(v-if="checkExecution.status === 'FAILED'")
      span Check has not been executed correctly.
      div
        code {{ checkExecution.result.exception }}

    div(v-else)
      //- Check execution failed, success in not defined
      div(v-if="checkExecution.status === 'Failed'")
        p This check has not been executed correctly. Verify you did set its parameters correctly.
        code(v-if="'exception' in checkExecution.result") {{ checkExecution.result.exception }}
      //- Chesk has been executed correcly: either success or not.
      div(v-else)
        p(v-if="checkExecution.success === true") No issues detected.
        div(v-else)
          v-alert(dark) <strong>{{ checkExecution.result.payload.length }}</strong> potential issue{{ checkExecution.result.payload.length > 1 ? 's' : '' }} detected.
          v-simple-table
            template(v-slot:default)
              thead
                tr
                  th(v-for="col in checkMetadata.resultFields" :key="col.id")
                    span {{ col.title }}
              tbody
                tr(v-for='item in checkExecution.result.payload' :key='item.id')
                  td(v-for="col in checkMetadata.resultFields" :key="col.id")
                    span {{ item[col.name] }}

    v-spacer

    v-row
      v-col.text-right
        v-btn.mt-4(small text
          @click="expandRawData = !expandRawData") Show raw data

    //- Raw data presented in a table
    div(v-if="expandRawData && inputDataNotEmpty")
      h4.overline.mt-10.mb-3 Input data
      v-simple-table
        template(v-slot:default)
          tbody
            tr(v-for='(value, name) in checkExecution.inputData' :key='name')
              td {{ name }}
              td
                code {{ value }}

    //- Raw results
    div(v-if="expandRawData")
      h4.overline.mt-10.mb-3 Results
      code {{ checkExecution.result }}
</template>

<script lang="ts">
  import Vue from 'vue';
  import { CheckExecution, CheckMetadata } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({
    props: {
      'checkExecution': Object as () => CheckExecution,
    },

    data: () => ({
      expandRawData: false,
    }),

    computed: {
      checkMetadata(): CheckMetadata {
        return _.find(this.$store.state.business.checksMetadata, {name: this.checkExecution.name});
      },

      inputDataNotEmpty(): boolean {
        return !_.isEmpty(this.checkExecution.inputData);
      },
    }

  });
</script>
