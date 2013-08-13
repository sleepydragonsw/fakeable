# -*- coding: utf-8 -*-

# Copyright 2013 Denver Coneybeare
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from __future__ import unicode_literals

################################################################################

__all__ = [
    "Fakeable",
    "set_fake_class",
    "set_fake_object",
    "unset",
    "clear",
]

################################################################################

class Fakeable(type):
    """
    A metaclass to be used by types that wish to be fakeable.
    """

    def __new__(cls, name, bases, dict_):
        if "__FAKE_NAME__" not in dict_:
            dict_["__FAKE_NAME__"] = name
        if "__FAKE_DOMAIN__" not in dict_:
            dict_["__FAKE_DOMAIN__"] = None
        return type.__new__(cls, name, bases, dict_)

    def __call__(self, *args, **kwargs):
        # use/create a fake instance, if one is registered
        try:
            fake_domain = fakes[self.__FAKE_DOMAIN__]
        except KeyError:
            pass
        else:
            try:
                instance = fake_domain.get(*args, **kwargs)
            except fake_domain.FakeNotFound:
                pass
            else:
                return instance

        # no fake instance was registered; create a real instance
        instance = type(self, *args, **kwargs)
        return instance

################################################################################

class FakeFactory(object):

    def __init__(self):
        self.fake_factories = {}

    def set_fake_class(self, name, value):
        entry = FakeClassEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def set_fake_object(self, name, value):
        entry = FakeObjectEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def unset(self, name):
        try:
            del self.fake_factories[name]
        except KeyError:
            return False
        else:
            return True

    def clear(self):
        self.fake_factories.clear()

    def get(self, name, *args, **kwargs):
        try:
            entry = self.fake_factories[name]
        except KeyError:
            raise self.FakeNotFound()
        else:
            instance = entry.get(*args, **kwargs)
            return instance

    class FakeNotFound(Exception):
        pass

################################################################################

class FakeEntry(object):

    def __init__(self, fake_factory, name):
        self.fake_factory = fake_factory
        self.name = name

    def unregister(self):
        self.fake_factory.unset(self.name)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unregister()

################################################################################

class FakeObjectEntry(FakeEntry):

    def __init__(self, fake_factory, name, value):
        super(FakeObjectEntry, self).__init__(fake_factory, name)
        self.value = value

    def get(self, *args, **kwargs):
        return self.value

################################################################################

class FakeClassEntry(FakeEntry):

    def __init__(self, fake_factory, name, value):
        super(FakeClassEntry, self).__init__(fake_factory, name)
        self.value = value

    def get(self, *args, **kwargs):
        instance = self.value(*args, **kwargs)
        return instance

################################################################################

default_fake_factory = FakeFactory()

# expose the methods of the default FakeFactory as module-level functions
set_fake_class = default_fake_factory.set_fake_class
set_fake_object = default_fake_factory.set_fake_object
unset = default_fake_factory.unset
clear = default_fake_factory.clear

# the different "domains" of fake objects
fakes = {None: default_fake_factory}

# no need to keep default_fake_domain around as a module-level attribute
del default_fake_factory

################################################################################
