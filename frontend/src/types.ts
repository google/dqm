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

export enum Colors {
  Green = '#34A853',
  Red = '#EA4335',
  Orange = '#FBBC04',
  Blue = '#4285F4',
}

export enum Status {
  Created = 0,
  Running = 1,
  Done = 2,
  Failed = 3
}

export interface AppSettings {
  authorizedEmails: string;
  gaServiceAccount: string;
}

export interface FatalError {
  text: string;
  details: object;
}

export interface Color {
  name: string;
}

export interface Snackbar {
  show: boolean;
  text: string;
}

export interface Theme {
  name: string;
  color: string;
  icon: string;
}

export interface Platform {
  name: string;
  color: string;
  icon: string;
}

export interface Template {
  label: string;
  disabled?: boolean;
}

export interface TreeViewItem {
  id: string;
  name: string;
  color: string;
  icon: string;
  children?: Array<TreeViewItem>;
}

export interface Parameter {
  name: string;
  title: string;
  data_type: string;
  default: string;
  delegate: boolean;
}

export interface ResultField {
  data_type: string;
  name: string;
  title: string;
}

export interface CheckMetadata {
  name: string;
  title: string;
  description: string;
  theme: string;
  platform: string;
  ga_level: string;
  parameters: Array<Parameter>;
  resultFields: Array<ResultField>;
}

export interface Check {
  id: number;
  name: string;
  active: boolean;
  comments: string;
  checkMetadata: CheckMetadata;
  paramValues: Map<string, any>;
}

export interface SuiteCreationData {
  name: string;
  templateId: string;
}

export interface CheckExecutionResult {
  success: boolean;
  payload: Map<string, any>; // À confirmer
}

export interface CheckExecution {
  id: number;
  name: string;
  title: string; // À virer (mettre une référence à CheckMetadata)
  status: Status;
  success: boolean;
  inputData: Map<string, any>;
  result: CheckExecutionResult;
}

export interface SuiteExecution {
  id: number;
  success: boolean;
  executed: string;
  checkExecutions: Array<CheckExecution>;
}

export interface GaScope {
  viewId: string;
  webPropertyId: string;
  accountId: string;
}

export interface GaParams {
  startDate: string;
  endDate: string;
  scope: Array<GaScope>;
}

export interface Suite {
  id: number | null;
  name: string;
  created: string;
  updated: string;
  checks: Array<Check>;
  executions: Array<SuiteExecution>;
  gaParams: GaParams;
}

// A simplified version of the Suite interface to avoid deep database lookups
// for simple suites listing display.
export interface SuitePreview {
  id: number | null;
  name: string;
  created: string;
  updated: string;
  lastExecutionSuccess: boolean | null;
}

export interface View {
  id: string;
  name: string;
  accountId: string;
  webPropertyId: string;
  websiteUrl: string;
  type: string;
  eCommerceTracking: boolean;
  enhancedECommerceTracking: boolean;
  botFilteringEnabled: boolean;
  excludeQueryParameters: string;
  siteSearchQueryParameters: string;
  stripSiteSearchQueryParameters: boolean;
}

export interface WebProperty {
  id: string;
  name: string;
  accountId: string;
  websiteUrl: string;
  views: Array<View>;
}

export interface Account {
  id: string;
  name: string;
  webProperties: Array<WebProperty>;
}