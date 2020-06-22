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

  v-navigation-drawer(
    v-model='$store.state.ui.drawer'
    app
    clipped)
    v-list(shaped)

      v-list-item(to='/')
        v-list-item-action
          v-icon mdi-view-dashboard-outline
        v-list-item-content
          v-list-item-title Dashboard

      v-list-item(to='/suites')
        v-list-item-action
          v-icon mdi-bug-check-outline
        v-list-item-content
          v-list-item-title My suites

      v-list-item(to='/settings')
        v-list-item-action
          v-icon mdi-cog
        v-list-item-content
          v-list-item-title Settings


      //- v-list-item(to='/settings')
      //-   v-list-item-action
      //-     v-icon mdi-settings
      //-   v-list-item-content
      //-     v-list-item-title Settings


      //- v-list-group(prepend-icon='mdi-bug-check-outline')
      //-   template(v-slot:activator)
      //-     v-list-item-title Check suites
      //-   v-list-item(to='/suites')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title My suites
      //-   v-list-item(to='/suites/new')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title New

      //- v-divider

      //- v-list-group(prepend-icon='mdi-security')
      //-   template(v-slot:activator)
      //-     v-list-item-title Trustful
      //-   v-list-item(to='pii')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title PII in URI
      //-   v-list-item(to='parameters')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title Non-useful URI parameters
      //-   v-list-item(to='trafic-origin')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title Trafic origin

      //- v-list-group(prepend-icon='mdi-database-search')
      //-   template(v-slot:activator)
      //-     v-list-item-title Insightful
      //-   v-list-item(to='custom-dims')
      //-     v-list-item-action
      //-       v-icon
      //-     v-list-item-content
      //-       v-list-item-title Custom dims

      //- v-list-item(disabled)
      //-   v-list-item-action
      //-     v-icon mdi-chart-timeline-variant
      //-   v-list-item-content
      //-     v-list-item-title Monitored

</template>

<script>
  export default {

  };
</script>
