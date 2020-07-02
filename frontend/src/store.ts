/**
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { AppSettings, FatalError, Theme, Platform, Template, Snackbar, Colors, Suite, Account, CheckMetadata, Check, GaParams, GaScope, SuiteExecution } from '@/types';

import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';
import _ from 'lodash';

Vue.use(Vuex);

// Axios is used for HTTP calls, and must be configured to honor Django CSRF
// verifications.
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'


interface UiState {
  readonly version: string;
  readonly debug: boolean;
  readonly feedbackFormUrl: string;
  readonly themes: Record<string, Theme>;
  readonly platforms: Record<string, Platform>;
  readonly templates: Record<string, Template>;
  readonly colors: Record<string, string>;
  appSettings: AppSettings;
  drawer: boolean;
  snackbar: Snackbar;
  fatalError?: FatalError;
}

interface BusinessState {
  suite: Suite;
  accounts: Array<Account>;
  checksMetadata: Array<CheckMetadata>;
}


export default new Vuex.Store({
  modules: {

    business: {
      state: {
        suite: {
          id: null,
          name: '',
          created: '',
          updated: '',
          checks: [],
          executions: [],
          gaParams: {
            startDate: '',
            endDate: '',
            scope: []
          }
        },
        accounts: [],
        checksMetadata: [],
      } as BusinessState,

      mutations: {
        updateSuite: (state, value: Suite) => {
          state.suite = value;
        },
        addSuiteExecution: (state, value: SuiteExecution) => { state.suite.executions.push(value); },
        addCheckToSuite: (state, check: Check) => {state.suite.checks.push(check)},
        updateCheck: (state, value: Check) => {
          state.suite.checks = _.map(state.suite.checks, (check: Check) => check.id == value.id ? value : check);
        },
        deleteCheck: (state, value: Check) => {
          state.suite.checks = _.reject(state.suite.checks, {'id': value.id} );
        },
        updateGaParams: (state, value: GaParams) => {state.suite.gaParams = value;},
        updateGaAccounts: (state, value) => {state.gaAccounts = value;},
        updateChecksMetadata: (state, value) => {state.checksMetadata = value;}
      },

      getters: {
        selectedViews: state => state.suite.gaParams.scope.map((item: GaScope) => item.viewId),
        suiteChecks: state => state.suite.checks,
      },

      actions: {
        async fetchCache({commit}) {
          try {
            const response = await axios.get(`/api/cache`);
            commit('updateGaAccounts', response.data.cache.gaAccounts);
          } catch(error) {
            commit('updateFatalError', error);
          }
        },

        async fetchGaAccounts({commit}) {
          try {
            const response = await axios.get(`/api/gaaccounts`)
            commit('updateGaAccounts', response.data.gaAccounts);
          }
          catch(error) {
            commit('updateFatalError', error)
          }
        },

        async fetchChecksMetadata({commit}) {
          try {
            const response = await axios.get(`/api/checks`)
            commit('updateChecksMetadata', response.data.checksMetadata);
          }
          catch(error) {
            commit('updateFatalError', error)
          }
        },

        async fetchSuites({commit}) {
          try {
            const response = await axios.get(`/api/suites/`, {});
            return response.data.suites;
          }
          catch(error) {
            commit('updateFatalError', error)
          }
        },

        async fetchSuite({commit}, {id}) {
          try {
            const response = await axios.get(`/api/suites/${id}`, {});
            commit('updateSuite', response.data.suite);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error);
          }
        },

        async createSuite({commit}, params) {
          try {
            const response = await axios.post(`/api/suites/`, params);
            return response.data.id;
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async updateSuite({commit}, suite) {
          try {
            await axios.put(`/api/suites/${suite.id}`, suite);
            commit('updateSuite', suite);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async deleteSuite({commit}, {suiteId}) {
          try {
            await axios.delete(`/api/suites/${suiteId}`);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async createCheck({commit, state}, checkName) {
          try {
            const response = await axios.post(`/api/suites/${state.suite.id}/checks`, {name: checkName});
            commit('addCheckToSuite', response.data.check);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async updateCheck({commit, state}, check) {
          try {
            await axios.put(`/api/suites/${state.suite.id}/checks/${check.id}`, check);
            commit('updateCheck', check);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async deleteCheck({commit, state}, check) {
          try {
            await axios.delete(`/api/suites/${state.suite.id}/checks/${check.id}`);
            commit('deleteCheck', check);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async updateGaParams({commit, state}, gaParams) {
          try {
            await axios.put(`/api/suites/${state.suite.id}`, state.suite);
            commit('updateGaParams', gaParams);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async runSuite({commit, state}) {
          try {
            const response = await axios.post(`/api/suites/${state.suite.id}/run`);
            const suiteExecution: SuiteExecution = response.data.result;
            commit('addSuiteExecution', suiteExecution);
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async fetchChecksStats({commit}) {
          try {
            const response = await axios.get(`/api/checks/stats`);
            return response.data.result;
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

        async fetchSuitesStats({commit}) {
          try {
            const response = await axios.get(`/api/suites/stats`);
            return response.data.result;
          }
          catch(error) {
            // TODO: Should return an error instead of dispatching a fatalError.
            commit('updateFatalError', error)
          }
        },

      },
    },

    ui: {
      state: {
        version: '0.3.1',
        debug: false,
        feedbackFormUrl: 'https://forms.gle/tZ1A7sPKf1QR4zP26',
        themes: {
          generic: {name: 'Generic', color: 'grey lighten-1', icon: 'mdi-console-line'},
          trustful: {name: 'Trustful', color: 'pink lighten-3', icon: 'mdi-security'},
          insightful: {name: 'Insightful', color: 'deep-purple lighten-3', icon: 'mdi-database-search'},
          monitored: {name: 'Monitored', color: 'teal lighten-3', icon: 'mdi-chart-timeline-variant'},
        },
        platforms: {
          generic: {name: 'Generic', color: 'grey', icon: 'mdi-google'},
          ga: {name: 'Google Analytics', color: 'grey', icon: 'mdi-google-analytics'},
          ads: {name: 'Google Ads', color: 'grey', icon: 'mdi-google-ads'},
        },
        templates: {
          empty: {label: 'Don\'t know yet, just start with an empty suite!', disabled: false},
          trustful: {label: 'Is my data trustful?', disabled: false},
          insightful: {label: 'Is my data insightful?', disabled: false},
          monitored: {label: 'Is my data monitored?', disabled: true},
        },
        colors: {
          green: Colors.Green,
          red: Colors.Red,
          orange: Colors.Orange,
          blue: Colors.Blue,
        },

        drawer: true,
        snackbar: {
          show: false,
          text: '',
        },
        appSettings: {
          authorizedEmails: '',
          gaServiceAccount: ''
        }
      } as UiState,

      mutations: {
        sidebar: (state) => { state.drawer = !state.drawer; },
        updateFatalError: (state, error) => { Vue.set(state, 'fatalError', {text: error.response.config.url, details: error.response}); },
        updateAppSettings: (state, value: AppSettings) => { state.appSettings = value; },
      },

      getters: {
        platform: (state) => (name: string) => {
          if(name in state.platforms) {
            return state.platforms[name];
          } else {
            return state.platforms['generic'];
          }
        },

        theme: (state) => (name: string) => {
          if(name in state.themes) {
            return state.themes[name];
          } else {
            return state.themes['generic'];
          }
        },
      },

      actions: {
        showMessage: ({state}, message) => {
          state.snackbar.text = message;
          state.snackbar.show = true;
        },

        async fetchAppSettings({commit}) {
          try {
            const response = await axios.get(`/api/appsettings`);
            commit('updateAppSettings', response.data.appSettings);
          }
          catch(error) {
            commit('updateFatalError', error)
          }
        },

      },
    }

  }
});
