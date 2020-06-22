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
    v-expansion-panel-header
      v-row(no-gutters)
        v-col(cols='11')
          v-checkbox(
            v-model='check.active'
            @change="$store.dispatch('updateCheck', check)"
            @click.native='checkBoxOverride($event)'
            :label='checkMetadata.title')
        v-col(cols='1')
          v-icon.pt-6(v-if="checkMetadata.platform=='ga' && checkMetadata.ga_level == 'view'" :color="$store.state.ui.colors.orange") mdi-alpha-v-circle-outline
          v-icon.pt-6(v-if="checkMetadata.platform=='ga' && checkMetadata.ga_level == 'property'" :color="$store.state.ui.colors.green") mdi-alpha-p-circle-outline
          v-icon.pt-6(v-if="checkMetadata.platform=='ga' && checkMetadata.ga_level == 'account'" :color="$store.state.ui.colors.blue") mdi-alpha-a-circle-outline

    v-expansion-panel-content
      div
        v-alert(dark text color="grey")
          div.small {{ checkMetadata.description }}
          div(v-if="checkMetadata.platform=='ga'").caption This check operates at {{ checkMetadata.ga_level }} level.

        div(v-if="visibleParameters.length > 0")
          h3.subtitle-2.pt-4.pb-3 Parameters

          v-row(justify="space-between")
            v-col(cols="12" md="12")
              v-form
                v-text-field(
                  v-for="p in visibleParameters"
                  v-model="check.paramValues[p.name]"
                  @input="$store.dispatch('updateCheck', check)"
                  :key="p.id"
                  :label="p.title ? p.title : p.name"
                  :placeholder="placeholder(p.data_type)"
                  outlined)

        v-btn(
          @click="$store.dispatch('deleteCheck', check)"
          depressed
          small)
          | Remove

</template>

<script lang="ts">
  import Vue from 'vue';
  import { Check, CheckMetadata, Parameter } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({
    props: {
      'checkId': Number as () => number,
    },

    computed: {
      check(): Check { return _.find(this.$store.state.business.suite.checks, {id: this.checkId}); },
      checkMetadata(): CheckMetadata { return _.find(this.$store.state.business.checksMetadata, {name: this.check.name}) },
      // Delegated parameters should not appear in the UI, and will be
      // populated automatically from other parts of the app (e.g. Scopes).
      visibleParameters(): Array<Parameter> { return _.filter(this.checkMetadata.parameters, {delegate: false}); }
    },

    methods: {
      checkBoxOverride: (e: any) => { e.cancelBubble = true; },
      placeholder: (dataType: string) => {
        switch(dataType) {
          case 'list': return 'Enter comma separated list of items, e.g.: a,b,c';
          case 'boolean': return 'Enter true of false';
          case 'date': return 'Enter a date, e.g.: 2000-01-01';
          case 'datetime': return 'Enter a date and time, e.g.: 2000-01-01';
          case 'int': return 'Enter a number';
          default: return 'Enter a text value';
        }
      },
    }

  });
</script>
