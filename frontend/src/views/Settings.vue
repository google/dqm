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
    v-card

      v-list(three-line subheader)
        v-row(no-gutters)
          v-col
            v-subheader GA credentials
          v-spacer
          v-col
            v-subheader.float-right
              v-btn(color="primary" @click="checkAccounts" text :loading='loading') Refresh list

        v-list-item
          v-list-item-content
            v-list-item-title Authorized GA accounts

            div.mt-2
              div(v-if="loading")
                v-skeleton-loader.float-left.mr-2(type='chip')
                v-skeleton-loader.float-left.mr-2(type='chip')
                v-skeleton-loader(type='chip')
              div(v-else)
                v-tooltip(bottom v-for="a in $store.state.business.gaAccounts" :key="a.id" )
                  template(v-slot:activator='{ on }')
                    v-chip.mr-2(color="primary" v-on='on' outlined) {{ a.name }}
                  span {{ a.id }}

        v-list-item
          v-list-item-content
            v-list-item-title Service account to use

            v-row
              v-col(cols="5")
                v-text-field(
                  v-model="$store.state.ui.appSettings.gaServiceAccount"
                  persistent-hint
                  outlined
                  dense
                  ref="textToCopy")
              v-col
                v-btn(@click="copyText" icon)
                  v-icon mdi-content-copy


      v-divider

      v-list(three-line subheader)
        v-subheader Who has access?
        v-list-item
          v-list-item-content
            v-list-item-title {{ $store.state.ui.appSettings.authorizedEmails }}

      v-divider

      v-list(three-line subheader)
        v-subheader Disclaimer
        v-list-item
          v-list-item-content
            p.grey--text(style="line-height: 1.4em") {{ disclaimer }}


</template>

<script lang="ts">
  import Vue from 'vue';

  export default Vue.extend({
    data () {
      return {
        loading: false,
        disclaimer: 'Copyright 2019 Google LLC. This solution, including any related sample code or data, is made  available on an “as is,” “as available,” and “with all faults” basis, solely for illustrative purposes, and without warranty or representation of any kind. This solution is experimental, unsupported and provided solely for your convenience. Your use of it is subject to your agreements with Google, as applicable, and may constitute a beta feature as defined under those agreements. To the extent that you make any data available to Google in connection with your use of the solution, you represent and warrant that you have all necessary and appropriate rights, consents and permissions to permit Google to use and process that data.  By using any portion of this solution, you acknowledge, assume and accept all risks, known and unknown, associated with its usage, including with respect to your deployment of any portion of this solution in your systems, or usage in connection with your business, if at all.',
      };
    },

    methods: {
      async checkAccounts() {
        this.loading = true;
        await this.$store.dispatch('fetchGaAccounts');
        this.loading = false;
      },

      copyText() {
        const textToCopy = (this.$refs.textToCopy as Record<string, any>).$el.querySelector('input');
        textToCopy.select();
        document.execCommand('copy');
        this.$store.dispatch('showMessage', 'Copied!');
      }
    }

  });
</script>
