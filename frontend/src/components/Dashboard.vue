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
    v-row

      v-col(lg="12")
        v-card(class="mx-auto" flat outlined :loading="!suitesStats.length")
          v-card-title
            v-icon(left color="grey lighten-2") mdi-chart-timeline-variant
            span.title.font-weight-light Suites execution history

          v-card-text
            GChart(
              v-if="suitesStats.length"
              type="AreaChart"
              :data="suitesStats"
              :options="chartOptions")

      v-col(lg="12")
        v-card(class="mx-auto" flat outlined :loading="!checksStats.length")
          v-card-title
            v-icon(left color="grey lighten-2") mdi-chart-timeline-variant
            span.title.font-weight-light Checks execution history

          v-card-text
            GChart(
              v-if="checksStats.length"
              type="AreaChart"
              :data="checksStats"
              :options="chartOptions")

</template>


<script lang="ts">
  import Vue from 'vue';
  import { GChart } from 'vue-google-charts';

  export default Vue.extend({
    components: {
      GChart
    },

    data () {
      return {
        checksStats: [],
        suitesStats: [],

        chartOptions: {
          colors: [
            this.$store.state.ui.colors.blue,
            this.$store.state.ui.colors.green,
            this.$store.state.ui.colors.red,
            this.$store.state.ui.colors.orange
          ],
          legend: {position: 'bottom'},
          hAxis: {
            textColor: '#bbb',
            gridlines: {
              color: '#eee'
            },
            baselineColor: '#ccc'
          },
          vAxis: {
            textColor: '#bbb',
            gridlines: {
              color: '#eee'
            },
            baselineColor: '#ccc',
            viewWindow:{
              min: 0
            }
          },
        }
      };
    },

    created: async function() {
      this.checksStats = await this.$store.dispatch('fetchChecksStats');
      this.suitesStats = await this.$store.dispatch('fetchSuitesStats');
    },

  });
</script>
