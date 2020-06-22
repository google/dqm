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

"""App config.
"""

from importlib import import_module
import inspect
import pkgutil
import sys

from django.apps import AppConfig
from dqm.checks import *


class DqmConfig(AppConfig):
  name = 'dqm'
  checks = {}

  def ready(self):
    """Here we inspect the `checks` module to discover all available check
    classes.

    Every check class name should contain the 'Check' word. Valid examples are:
    - MyCheck
    - CheckSomething

    The `checks` class parameter is added to DqmConfig, containing a dictionnary
    like:
    {
      'MyCheck': <class 'dqm.checks.my-check-file.MyCheck'>,
      # ...
    }
    """
    checks = {}
    checks_module = sys.modules['dqm.checks']

    for (module_loader, name, ispkg) in pkgutil.iter_modules(
        checks_module.__path__):
      sub_module_name = 'dqm.checks.{}'.format(name)
      import_module(sub_module_name)
      sub_module = sys.modules[sub_module_name]
      classes = inspect.getmembers(sub_module, inspect.isclass)

      check_classes = [m for m in classes if (m[1].__module__ ==
        sub_module.__name__ and 'Check' in [
          a.__name__ for a in m[1].__bases__])]

      for cc in check_classes:
        checks[cc[0]] = cc[1]

    self.__class__.checks = checks
