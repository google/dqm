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
      h1.mb-3.overline {{ suite.name }}

      v-stepper.mb-10(
        v-model="currentStep"
        alt-labels)
        v-stepper-header
          v-stepper-step(step=1 editable) Scope
          v-divider
          v-stepper-step(step=2 editable) Checks
          v-divider
          v-stepper-step(step=3 editable) Global settings
          v-divider
          v-stepper-step(step=4 editable) Results

    template(v-if="currentStep==1")
      StepScope

    template(v-if="currentStep==2")
      StepChecks

    template(v-if="currentStep==3")
      StepSettings

    template(v-if="currentStep==4")
      StepReview

</template>

<script lang="ts">
  import Vue from 'vue';
  import { Suite } from '@/types';
  import StepScope from '@/components/suite/StepScope.vue';
  import StepChecks from '@/components/suite/StepChecks.vue';
  import StepSettings from '@/components/suite/StepSettings.vue';
  import StepReview from '@/components/suite/StepReview.vue';

  export default Vue.extend({
    components: {
      StepScope,
      StepChecks,
      StepSettings,
      StepReview,
    },

    data: () => ({
      currentStep: 1,
      isRunning: false,
    }),

    computed: {
      suite: {
        get(): Suite { return this.$store.state.business.suite; },
      },
    },

    created: function() {
      this.$store.dispatch('fetchSuite', {id: this.$route.params.id});
    },

  });
</script>
