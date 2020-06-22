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
    v-row.pa-4(justify='space-between')
      v-col
        v-treeview(
          v-model="selectedViews"
          @input="updateSuiteSelectedViews"
          :items="accountsTree"
          :open="opened"
          open-on-click
          selectable
          dense)
          template(v-slot:prepend="{ item, open }")
            // Add the (A), (P) or (V) icon on the left of every item
            v-icon.ml-2(:color="item.color") {{ item.icon }}
          template(v-slot:append="{ item, open }")
            // Add the identifier of the item on the right of every item
            v-chip(:color="item.color" outlined small label) {{ item.id }}

</template>

<script lang="ts">
  import Vue from 'vue';
  import { Account, GaScope, WebProperty, View, TreeViewItem, Suite } from '@/types';
  import _ from 'lodash';

  export default Vue.extend({

    data: () => ({
      accountsTree: [] as Array<TreeViewItem>,
      opened: [] as Array<string>,

      selectedViews: [],
      unwatchSelectedViews: Function(),
    }),

    created() {
      this.accountsTree = this.createAccountsTree();

      // For some reason, v-treeview selectable doens not syncrohnise well with
      // computed properties. To ensure data freshness in the component during
      // the whole StepScope lifecycle, we need to have selectedViews (list of
      // selected nodes) in the data object. Given the data source may not be
      // available when the component loads for the first time, we have to watch
      // for store.getters.selectedViews changes...
      this.selectedViews = this.$store.getters.selectedViews;
      this.unwatchSelectedViews = this.$store.watch(
        (state, getters) => getters.selectedViews,
        (newValue, oldValue) => {
          this.selectedViews = newValue;
        },
      );
    },

    beforeDestroy() {
      this.unwatchSelectedViews();
    },

    computed: {
      scope(): GaScope { return this.$store.state.business.suite.gaParams.scope; },
      accounts(): Array<Account> { return this.$store.state.business.gaAccounts; },
    },

    methods: {
      createAccountsTree(): Array<TreeViewItem> {
        return this.accounts.map((account: Account) => {
          return {
            id: account.id,
            name: account.name,
            icon: 'mdi-alpha-a-circle-outline',
            color: this.$store.state.ui.colors.blue,
            children: account.webProperties.map((property: WebProperty) => {
              return {
                id: property.id,
                name: property.name,
                icon: 'mdi-alpha-p-circle-outline',
                color: this.$store.state.ui.colors.green,
                children: property.views.map((view: View) => {
                  return {
                    id: view.id,
                    name: view.name,
                    icon: 'mdi-alpha-v-circle-outline',
                    color: this.$store.state.ui.colors.orange,
                  };
                })
              };
            })
          };
        });
      },

      updateSuiteSelectedViews(selectedViews: Array<string>) {
        const newScope: Array<GaScope> = [];
        _.forEach(this.accounts, (account) => {
          _.forEach(account.webProperties, (webProperty) => {
            _.forEach(webProperty.views, (view) => {
              if(_.includes(selectedViews, view.id)) {
                newScope.push({
                  viewId: view.id,
                  webPropertyId: webProperty.id,
                  accountId: account.id
                });
              }
            })
          })
        });
        // We don't want to trigger a commit if the scope hasn't changed.
        if(_.isEqual(newScope, this.scope)) {
          return;
        }
        const updatedSuite: Suite = _.clone(this.$store.state.business.suite);
        updatedSuite.gaParams.scope = newScope;
        this.$store.dispatch('updateSuite', updatedSuite);
      },
    }

  });
</script>

