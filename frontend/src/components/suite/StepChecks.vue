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
    ChecksLibrary(@checkAddedtoSuite="openCheckPanel")

    v-row.pa-6(justify="space-between")
      v-expansion-panels(v-model="openedPanels")
        v-expansion-panel(v-for="check in suiteChecks" :key="check.id")
          CheckItem(:checkId="check.id")

</template>

<script lang="ts">
  import Vue from 'vue';
  import ChecksLibrary from '@/components/suite/checks/ChecksLibrary.vue';
  import CheckItem from '@/components/suite/checks/CheckItem.vue';
  import { Check } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({
    components: {
      ChecksLibrary,
      CheckItem
    },

    data: () => ({
      openedPanels: null as number | null,
    }),

    computed: {
      suiteChecks(): Array<Check> { return this.$store.state.business.suite.checks; },
    },

    methods: {
      openCheckPanel(checkName: string) {
        this.openedPanels = _.findIndex(this.suiteChecks, {name: checkName})
      }
    }

  });
</script>
