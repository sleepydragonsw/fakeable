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
        # use the class name as the "name" of the fake, but allow the class
        # to override this name by setting __FAKE_NAME__
        try:
            __FAKE_NAME__ = dict_["__FAKE_NAME__"]
        except KeyError:
            dict_["__FAKE_NAME__"] = name
        else:
            # ensure that the __FAKE_NAME__ attribute of the class is hashable
            hash(__FAKE_NAME__)

        # create the type object with the possibly-slightly-modified dict
        type_ = type.__new__(cls, name, bases, dict_)
        return type_

    def __call__(self, *args, **kwargs):
        # try looking up the fake object by the class first
        try:
            instance = fake_factory.get(self, *args, **kwargs)
        except fake_factory.FakeNotFound:
            pass
        else:
            return instance

        # try looking up the fake object by name
        fake_name = self.__FAKE_NAME__
        try:
            instance = fake_factory.get(fake_name, *args, **kwargs)
        except fake_factory.FakeNotFound:
            pass
        else:
            return instance

        # no fake instance was registered; create a real instance
        instance = type.__call__(self, *args, **kwargs)
        return instance

################################################################################

class FakeFactory(object):
    """
    A database of fake objects.
    """

    def __init__(self):
        self.fake_factories = {}

    def set_fake_class(self, name, value):
        """
        Configures the class with the given name to create fake objects instead
        of real objects when created.  When an instance of the class of the
        given name is created a new instance of the given type will be created
        instead.

        Arguments:
            *name* (string or Fakeable)
                the name of the class, or the class itself, that will have fake
                instances created instead of real instances; if a string, this
                will be the name of the class or, if the class defines
                __FAKE_NAME__, the value of that class' __FAKE_NAME__ attribute.
            *value* (class)
                the class whose instances will be created in place of the real
                class; whatever arguments were given to the __init__() method
                of the real class will be passed on to the __init__() method of
                the created instance of this class.

        Returns a context manager that can be used as the target of a "with"
        statement; when the context of the "with" statement is exited the fake
        class will be automatically unregistered by a call to self.unset(name).
        """
        entry = FakeClassEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def set_fake_object(self, name, value):
        """
        Configures the class with the given name to always use a fake object
        instead of real objects when created.  When an instance of the class of
        the given name is created the given value will be returned instead.

        Arguments:
            *name* (string or Fakeable)
                the name of the class, or the class itself, that will have fake
                instances created instead of real instances; if a string, this
                will be the name of the class or, if the class defines
                __FAKE_NAME__, the value of that class' __FAKE_NAME__ attribute.
            *value* (object)
                the object to be returned in place of a new instance of the real
                class; whatever arguments were given to the __init__() method
                of the real class will be discarded.

        Returns a context manager that can be used as the target of a "with"
        statement; when the context of the "with" statement is exited the fake
        object will be automatically unregistered by a call to self.unset(name).
        """
        entry = FakeObjectEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def unset(self, name):
        """
        Unregisters a fake that was registered by a previous invocation of one
        of the sex_XXX() methods of this object.

        Arguments:
            *name* (string or Fakeable)
                the name of the class, or the class itself, whose fake is to be
                unregistered; if a string, this will be the name of the class
                or, if the class defines __FAKE_NAME__, the value of that class'
                __FAKE_NAME__ attribute.

        Returns True if a fake was indeed registered with the given name and
        was successfully unregistered.  Returns False if a fake was *not*
        registered with the given name and therefore this method did nothing.
        """
        try:
            del self.fake_factories[name]
        except KeyError:
            return False
        else:
            return True

    def clear(self):
        """
        Unregisters all fake objects that have been previously registered.
        """
        self.fake_factories.clear()

    def get(self, name, *args, **kwargs):
        """
        Gets or creates the fake object for a class.

        This method is the one used by the Fakeable metaclass to create the
        fake instances.  It should not normally be invoked directly.

        Arguments:
            *name* (string or Fakeable instance)
                the name of the class, or the class itself, whose fake object
                to get or create; if a string, this will be the name of the
                class or, if the class defines __FAKE_NAME__, the value of that
                class' __FAKE_NAME__ attribute.

        Returns the fake object for the class with the given name.
        Raises self.FakeNotFound if no fake was registered with the given name.
        """
        try:
            entry = self.fake_factories[name]
        except KeyError:
            raise self.FakeNotFound()
        else:
            instance = entry.get(*args, **kwargs)
            return instance

    class FakeNotFound(Exception):
        """
        Exception raised by get() if a fake is not found to be registered with
        the name that it is given.
        """
        pass

################################################################################

class FakeEntry(object):
    """
    An entry in the fake factory.
    This is an abstract base class, and must be subclassed and the get()
    method overridden to be meaningful.
    """

    def __init__(self, fake_factory, name):
        self.fake_factory = fake_factory
        self.name = name

    def unregister(self):
        self.fake_factory.unset(self.name)

    def get(self, *args, **kwargs):
        raise NotImplementedError("must be implemented by a subclass")

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unregister()

################################################################################

class FakeObjectEntry(FakeEntry):
    """
    An entry in the fake factory where a predefined object is returned when
    instances of the class are created.
    """

    def __init__(self, fake_factory, name, value):
        super(FakeObjectEntry, self).__init__(fake_factory, name)
        self.value = value

    def get(self, *args, **kwargs):
        return self.value

################################################################################

class FakeClassEntry(FakeEntry):
    """
    An entry in the fake factory where instances of a different class are to be
    created and returned when instances of the class are created.
    """

    def __init__(self, fake_factory, name, value):
        super(FakeClassEntry, self).__init__(fake_factory, name)
        self.value = value

    def get(self, *args, **kwargs):
        instance = self.value(*args, **kwargs)
        return instance

################################################################################

# the global FakeFactory instance
fake_factory = FakeFactory()

# expose the methods of the default FakeFactory as module-level functions
set_fake_class = fake_factory.set_fake_class
set_fake_object = fake_factory.set_fake_object
unset = fake_factory.unset
clear = fake_factory.clear

################################################################################
