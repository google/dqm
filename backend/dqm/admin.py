# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Admin classes for Django Admin site
"""

from django.contrib import admin

from .models import *


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
  pass


@admin.register(ApiCache)
class ApiCacheAdmin(admin.ModelAdmin):
  pass


@admin.register(GaParams)
class GaParamsAdmin(admin.ModelAdmin):
  list_display = ('scope', 'start_date', 'end_date')


@admin.register(CheckExecution)
class CheckExecutionAdmin(admin.ModelAdmin):
  list_display = ('check_ref', 'status', 'success', 'created')


class CheckExecutionInline(admin.TabularInline):
  model = CheckExecution
  fields = ('status', 'success', 'input_data_json', 'result_json')
  extra = 0


@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
  inlines = (CheckExecutionInline,)
  list_display = ('name', 'suite', 'active', 'created')
  list_filter = ('suite',)


class CheckInline(admin.TabularInline):
  model = Check
  exclude = ('comments',)
  extra = 0


class SuiteExecutionInline(admin.TabularInline):
  model = SuiteExecution
  extra = 0


class GaParamsInline(admin.TabularInline):
  model = GaParams
  extra = 0


@admin.register(Suite)
class SuiteAdmin(admin.ModelAdmin):
  inlines = (GaParamsInline, CheckInline, SuiteExecutionInline,)
  list_display = ('id', 'name',)

