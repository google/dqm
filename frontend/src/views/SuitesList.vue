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
      v-data-table.elevation-1(
        :headers="suitesDataTable.headers"
        :items="suites"
        :items-per-page="15"
        :loading="suitesDataTable.loading"
        no-data-text="You don't have any suite yet.")

        template(v-slot:item.status="{ item }")
          v-icon(v-if="item.lastExecutionSuccess === true" :color="$store.state.ui.colors.green") mdi-circle
          v-icon(v-if="item.lastExecutionSuccess === false" :color="$store.state.ui.colors.red") mdi-circle

        template(v-slot:item.name="{ item }")
          router-link(
            :to="{name: 'suite', params: {id: item.id}}")
            | {{ item.name }}

        template(v-slot:item.updated="{ item }")
          span {{ item.updated | formatDate() }}

        template(v-slot:item.action='{ item }')
          v-icon(@click='deleteItemConfirmation(item)') mdi-delete-outline

      v-dialog(v-model='deleteItemConfirmationModal' persistent max-width='400')
        v-card
          v-card-title.headline Confirm your action
          v-card-text
            p You are about to delete the complete suite "{{ selectedItem ? selectedItem.name : '' }}". It will also delete all its checks and settings.
          v-card-actions
            v-spacer
            v-btn(text @click='deleteItemConfirmationModal = false')
              | Cancel
            v-btn(text @click='deleteItem')
              | Confirm

</template>

<script lang="ts">
  import Vue from 'vue';
  import { SuitePreview } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({
    data: () => ({
      suites: [] as Array<SuitePreview>,
      selectedItem: null as SuitePreview | null,
      deleteItemConfirmationModal: false,
      suitesDataTable: {
        loading: true,
        headers: [
          {text: 'Status', value: 'status', width: '100px'},
          {text: 'Name', value: 'name'},
          // {text: 'Nbr checks', value: 'nbrChecks', align: 'end'},
          {text: 'Last update', value: 'updated', align: 'end'},
          {text: 'Actions', value: 'action', width: '100px'},
        ]
      }
    }),

    created: async function () {
      this.suites = await this.$store.dispatch('fetchSuites');
      this.suitesDataTable.loading = false;
    },

    methods: {
      deleteItemConfirmation(suite: SuitePreview) {
        this.selectedItem = suite;
        this.deleteItemConfirmationModal = true;
      },

      async deleteItem() {
        if(this.selectedItem) {
          await this.$store.dispatch('deleteSuite', {suiteId: this.selectedItem.id});
          this.$store.dispatch('showMessage', 'Suite has been deleted.');
          this.suites = _.reject(this.suites, {id: this.selectedItem.id})
          this.deleteItemConfirmationModal = false;
          this.selectedItem = null;
        }
      },
    }
  });
</script>
