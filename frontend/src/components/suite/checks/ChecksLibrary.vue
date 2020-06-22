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
    v-expansion-panels.mt-5(v-model="opened")
      v-expansion-panel
        v-expansion-panel-header.subtitle-2
          span Checks library

        v-expansion-panel-content
          v-text-field(
            v-model="filter"
            label="Filter checks")

          v-row
            v-col(cols="12" sm="4" md="3" v-for="checkMetadata in filteredChecksMetadata" :key="checkMetadata.id")
              v-card.mx-auto(outlined)
                v-list-item(three-line)
                  v-list-item-content
                    div.overline.mb-4
                      v-icon {{ $store.getters.platform(checkMetadata.platform).icon }}
                      span.pl-3 {{ $store.getters.platform(checkMetadata.platform).name }}
                    v-divider
                    v-list-item-title.mb-1 {{ checkMetadata.title }}
                    v-list-item-subtitle {{ checkMetadata.description }}

                v-card-actions
                  v-chip.ma-2(
                    small
                    :color="$store.getters.theme(checkMetadata.theme).color"
                    outlined)
                    v-icon(
                      left
                      small) {{ $store.getters.theme(checkMetadata.theme).icon }}
                    span {{ $store.getters.theme(checkMetadata.theme).name }}
                  v-spacer
                  v-btn(
                    depressed
                    small
                    @click="addCheck(checkMetadata.name)")
                    | Add
          v-row
            v-btn(
              v-if="!extendedViewActivated"
              @click="extendedViewActivated = !extendedViewActivated"
              small
              depressed
              block)
              | Show full list

</template>

<script lang="ts">
  import Vue from 'vue';
  import { Check, CheckMetadata } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({
    data: () => ({
      filter: '',
      opened: null as number | null,
      extendedViewActivated: false
    }),

    created() {
      this.opened = _.isEmpty(this.suiteChecks) ? 0 : null;
    },

    computed: {
      suiteChecks(): Array<Check> { return this.$store.state.business.suite.checks; },
      checksMetadata(): Array<CheckMetadata> { return this.$store.state.business.checksMetadata; },
      panelOpened(): boolean {return this.suiteChecks.length > 0 ? false : true; },

      /**
       * Filters the checksMetadata prop against:
       * - Check title
       * - Platform name
       * - Theme name
       *
       * The corresponding check shouldn't be in the suite yet.
       */
      filteredChecksMetadata(): Array<CheckMetadata> {
        const checksNotInSuite = _.reject(this.checksMetadata, (o) => _.includes(_.map(this.suiteChecks, (c) => c.name), o.name));
        const searchString = this.filter.toLowerCase();

        const filter = (cm: CheckMetadata): boolean => {
          return _.includes(cm.name.toLowerCase(), searchString)
            || _.includes(this.$store.getters.platform(cm.platform).name.toLowerCase(), searchString)
            || _.includes(this.$store.getters.theme(cm.theme).name.toLowerCase(), searchString)
        };

        const filtered: Array<CheckMetadata> = _.filter(checksNotInSuite, filter);
        return this.extendedViewActivated ? filtered : filtered.slice(0, 8);
      },
    },

    methods: {
      async addCheck(name: string) {
        this.opened = null;
        await this.$store.dispatch('createCheck', name);
        // Warn parent that check has been added (to open the panel)
        this.$emit('checkAddedtoSuite', name)
      }
    }

  });
</script>
