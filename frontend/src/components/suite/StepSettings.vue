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
    v-card(flat outlined)
      v-card-title.overline.mb-5 Time frame

      v-card-text
        v-row
          v-col(cols='12' sm='4' md='4')
            v-menu(ref='startDateMenu' :close-on-content-click='false' transition='scale-transition' offset-y min-width='290px'
              v-model='startDateMenu')
              template(v-slot:activator='{ on }')
                v-text-field(label='Start date' prepend-icon='mdi-event' v-on='on'
                  v-model='startDate')
              v-date-picker.flex-grow-1(no-title scrollable
                v-model='startDate')
                v-btn(text color='primary' @click='startDateMenu = false') OK

          v-col(cols='12' sm='4' md='4')
            v-menu(ref='endDateMenu' :close-on-content-click='false' transition='scale-transition' offset-y min-width='290px'
              v-model='endDateMenu' )
              template(v-slot:activator='{ on }')
                v-text-field(label='End date' prepend-icon='mdi-event' v-on='on'
                  v-model='endDate' )
              v-date-picker.flex-grow-1(no-title scrollable
                v-model='endDate' )
                v-btn(text color='primary' @click='endDateMenu = false') OK

</template>

<script lang="ts">
  import Vue from 'vue';
  import _ from 'lodash';

  export default Vue.extend({
    data: () => ({
      startDateMenu: null,
      endDateMenu: null,
    }),

    computed: {
      startDate: {
        get(): string { return this.$store.state.business.suite.gaParams.startDate; },
        set(value: string) {
          const updatedSuite = _.clone(this.$store.state.business.suite);
          updatedSuite.gaParams.startDate = value;
          this.$store.dispatch('updateSuite', updatedSuite);
        }
      },

      endDate: {
        get(): string { return this.$store.state.business.suite.gaParams.endDate; },
        set(value: string) {
          const updatedSuite = _.clone(this.$store.state.business.suite);
          updatedSuite.gaParams.endDate = value;
          this.$store.dispatch('updateSuite', updatedSuite);
        }
      },
    },

  });
</script>
