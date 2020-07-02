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
  v-dialog(
    v-model="show"
    persistent
    max-width="600px"
    @keydown.esc="close")
    v-card
      v-card-title
        span.headline New check suite

      v-card-text
        v-container
          v-row
            v-col(cols='12')
              v-form(v-model="formIsValid")
                v-text-field(
                  label="Name *"
                  v-model="suiteCreationData.name"
                  :rules="[v => !!v || 'A name is required']"
                  autofocus
                  required)

                p.mt-7 What is your focus?

                v-radio-group(v-model="suiteCreationData.templateId")
                  v-radio(
                    v-for="(tpl, id) in templates"
                    :key="id"
                    :label="tpl.label"
                    :value="id"
                    :disabled="tpl.disabled")
                    template(v-slot:label)
                      v-chip.mr-2(
                        v-if="tpl.id !== 'empty'"
                        small
                        :color="$store.getters.theme(id).color"
                        outlined)
                        v-icon(left small) {{ $store.getters.theme(id).icon }}
                        span {{ $store.getters.theme(id).name }}
                      span {{ tpl.label }}

      v-card-actions
        v-spacer
        v-btn(
          color='blue darken-1'
          text
          @click="close")
          | Cancel
        v-btn(
          :disabled="!formIsValid"
          color='blue darken-1'
          text
          @click="save")
          | Save

</template>


<script lang="ts">
  import Vue from 'vue';
  import { SuiteCreationData, Template } from '@/types';
  import _ from 'lodash';

  const suiteCreationDataDefault: SuiteCreationData = {
    name: '',
    templateId: 'empty'
  };

  export default Vue.extend({
    props: {
      show: Boolean as () => boolean
    },

    data: () => ({
      formIsValid: false,
      suiteCreationData: _.clone(suiteCreationDataDefault) as SuiteCreationData
    }),

    computed: {
      templates(): Array<Template> { return this.$store.state.ui.templates; },
    },

    methods: {
      async save() {
        const suiteId = await this.$store.dispatch('createSuite', this.suiteCreationData);
        this.$store.dispatch('showMessage', 'Your suite has been created, and is ready for setup!');
        this.suiteCreationData = _.clone(suiteCreationDataDefault);
        this.$router.push({name: 'suite', params: {id: suiteId}});
        this.close();
      },

      close() {
        this.$emit('updateShowSuiteCreationDialog', false);
      }
    },

  });
</script>
