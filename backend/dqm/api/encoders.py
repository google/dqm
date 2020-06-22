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

"""IO encoders used in DQM.
"""

from django.core.serializers.json import DjangoJSONEncoder
from dqm.check_bricks import DataType


class DqmApiEncoder(DjangoJSONEncoder):
  """A custom encoder for API JSON responses that converts DataType enums
  into their string value.
  """
  def default(self, o):
    if isinstance(o, DataType):
      return o.value
    else:
      return super().default(o)
