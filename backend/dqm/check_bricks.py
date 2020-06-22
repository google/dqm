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

from abc import ABC
from dataclasses import asdict, dataclass
from datetime import date, datetime
from distutils.util import strtobool
from enum import Enum
from typing import Any, Dict, List, Optional

from dqm import errors


class DataType(Enum):
  STRING = 'str'
  LIST = 'list'
  BOOLEAN = 'boolean'
  DATE = 'date'
  DATETIME = 'datetime'
  INT = 'int'


class Platform(Enum):
  Generic = 'generic'
  Ga = 'ga'
  Ads = 'ads'


class Theme(Enum):
  Generic = 'generic'
  Trustful = 'trustful'
  Insightful = 'insightful'
  Monitored = 'monitored'


class GaLevel(Enum):
  Account = 'account'
  Property = 'property'
  View = 'view'


@dataclass
class ResultField:
  name: str
  data_type: DataType
  title: Optional[str] = None


@dataclass
class Result:
  payload: List
  success: bool = False


@dataclass
class Parameter:
  """
  >>> Parameter(data_type=DataType.DATE, name='').validate('2020-01-01')
  datetime.date(2020, 1, 1)
  >>> Parameter(data_type=DataType.DATE, default=date(1999, 1, 1), name='').validate()
  datetime.date(1999, 1, 1)
  >>> Parameter(data_type=DataType.BOOLEAN, default=True, name='').validate(False)
  False
  >>> Parameter(data_type=DataType.BOOLEAN, default=True, name='').validate()
  True
  >>> Parameter(data_type=DataType.LIST, default=[], name='').validate()
  []
  >>> Parameter(data_type=DataType.LIST, name='').validate([])
  []
  >>> Parameter(data_type=DataType.LIST, name='').validate('1,2,3')
  ['1', '2', '3']
  >>> asdict(Parameter(data_type=DataType.STRING, name=''))
  {'name': '', 'data_type': 'str', 'title': '', 'default': None}
  """
  name: str
  data_type: DataType
  title: str = ''
  default: Any = None
  delegate: bool = False

  def __post_init__(self) -> None:
    self._validate_default_value()

  def _validate_default_value(self) -> None:
    default = self.default
    if default != None:
      if (self.data_type == DataType.DATE and type(default) != date
        or self.data_type == DataType.DATETIME and type(default) != datetime
        or self.data_type == DataType.STRING and type(default) != str
        or self.data_type == DataType.LIST and type(default) != list
        or self.data_type == DataType.INT and type(default) != int
        or self.data_type == DataType.BOOLEAN and type(default) != bool):
        raise errors.BadDefaultValueTypeError(
          name=self.name,
          expected=self.data_type,
          got=type(default))

  def cast(self, value: Any) -> Any:
    """Cast a value according to parameter data type.
    """
    if self.data_type == DataType.DATE and not isinstance(value, date):
      if value:
        return datetime.strptime(value, '%Y-%m-%d').date()
      else:
        return datetime.now().date()
    if self.data_type == DataType.DATETIME and not isinstance(value, datetime):
      if value:
        return datetime.strptime(value, '%Y-%m-%d')
      else:
        return datetime.now()
    elif self.data_type == DataType.LIST and not isinstance(value, list):
      return [] if value in ('', None) else value.split(',')
    elif self.data_type == DataType.BOOLEAN and not isinstance(value, bool):
      return False if value in ('', None) else bool(strtobool(value))
    elif self.data_type == DataType.INT and not isinstance(value, int):
      return int(value)
    else:
      return value

  def validate(self, value: Any = None) -> Any:
    if value == None and self.default == None:
      raise errors.MissingParameterValueError(
        data_type=self.data_type,
        name=self.name)

    # Empty fields comming from UI actually contain an empty string.
    if value == '':
      value = None

    return self.cast(value) if value != None else self.cast(self.default)


class Check(ABC):
  """The base class for every check to inherit from.
  """
  name: str
  title: str
  description: str
  theme: Theme = Theme.Generic
  platform: Platform = Platform.Generic
  ga_level: GaLevel = GaLevel.View
  parameters: List[Parameter] = []
  result_fields: List[ResultField] = []

  @classmethod
  def _validate_metadata(cls):
    """Internal method used to verify that a check class declares all required
    metadata attributes.
    """
    required_attributes = ['title', 'description']
    for attr in required_attributes:
      if not attr in cls.__dict__:
        raise errors.MissingMetadata(check_name=cls.__name__, attr=attr)

    if not cls.result_fields:
      raise errors.NoResultField(check_name=cls.__name__)

  @classmethod
  def get_metadata(cls) -> Dict[str, Any]:
    """Build a dictionary of the check attributes, after having checked that all
    required metadata attributes have been declared in the check class.
    """
    cls._validate_metadata()

    attributes = {
      'name': cls.__name__,
      'title': cls.title,
      'description': cls.description,
      'theme': cls.theme.value,
      'platform': cls.platform.value,
      'ga_level': cls.ga_level.value,
    }

    try:
      attributes['parameters'] = [asdict(p) for p in cls.parameters]
    except:
      raise errors.BadParametersError(check_name=cls.__name__)

    try:
      attributes['resultFields'] = [asdict(rf) for rf in cls.result_fields]
    except:
      raise errors.BadResultFielsError(check_name=cls.__name__)

    return attributes

  def validate_values(self, values: Dict) -> Dict[str, Any]:
    """This method is intended to be called in the `run` method of each check
    class, in order to get a sanitized dictionnary of parameters and related
    values.

    Each parameter value is validated before beeing added to the result dict,
    and default values are set is needed.
    """
    valid = {}

    for p in self.parameters:
      valid[p.name] = p.validate(values[p.name] if p.name in values else None)

    return valid

  def run(self, params: List) -> Result:
    """This abstract method has to be overiden for each check class, and should
    contain all the testing logic, returning a populated `Result` object.
    """
    raise errors.CheckNotImplementedError(
      check_name=self.get_metadata()['name'])
