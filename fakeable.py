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


__all__ = [
    "Fakeable",
    "set_fake_class",
    "set_fake_object",
    "unset",
    "clear",
    "FakeableCleanupMixin",
]


class Fakeable(type):
    """
    A metaclass to be used by types that wish to be fakeable.

    In order to make a class fakeable,
    all that needs to be done is set *fakeable.Fakeable* as its metaclass.
    In Python 2, this done by setting the special attribute
    ``__metaclass__ = fakeable.Fakeable`` in the class definition.
    In Python 3, this is done by specifying ``metaclass=fakeable.Fakeable``
    in the base class list of the class definition.

    Python 2 example::

        class HttpDownloader(object):
            __metaclass__ = fakeable.Fakeable
            ...

    Python 3 example::

        class HttpDownloader(metaclass=fakeable.Fakeable):
            ...

    If you have the third-party ``six`` module installed,
    then you can do this in a way that works in both Python 2 and Python 3::

        class HttpDownloader(six.with_metaclass(fakeable.Fakeable)):
            ...

    The name used in the *fakeable* module functions to refer to this class
    is simply the name of the class.
    This value is stored in the ``__FAKE_NAME__`` attribute of the class.
    If a class explicitly defines a ``__FAKE_NAME__`` attribute
    then that value will be used instead of the default.
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


class FakeFactory(object):
    """
    A database of fake objects.
    """

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


# the global FakeFactory instance
fake_factory = FakeFactory()


def set_fake_class(name, value):
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
    fake_factory.set_fake_class(name, value)


def set_fake_object(name, value):
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
    fake_factory.set_fake_object(name, value)


def unset(name):
    """
    Unregisters a fake that was registered by a previous invocation of one
    of the sex_XXX() functions.

    Arguments:
        *name* (string or Fakeable)
            the name of the class, or the class itself, whose fake is to be
            unregistered; if a string, this will be the name of the class
            or, if the class defines __FAKE_NAME__, the value of that class'
            __FAKE_NAME__ attribute.

    Returns True if a fake was indeed registered with the given name and
    was successfully unregistered.  Returns False if a fake was *not*
    registered with the given name and therefore this function did nothing.
    """
    fake_factory.unset(name)


def clear():
    """
    Unregisters all fake objects that have been previously registered.
    """
    fake_factory.clear()


class FakeableCleanupMixin(object):
    """
    A convenience class that can be inherited by unit test classes so that
    fakes are automatically cleaned up before and after each test runs.
    This helps prevent fake objects inadvertently leaking into other test
    cases, which can cause difficult-to-diagnose behaviour when it happens.

    This class is intended to be subclassed by other classes that also inherit
    from ``unittest.TestCase``.
    It defines :meth:`~fakeable.FakeableCleanupMixin.setUp` and
    :meth:`~fakeable.FakeableCleanupMixin.tearDown`, both of which simply
    invoke :func:`fakeable.clear` and the method of the same name in the
    superclass.

    *Example*: using this "mixin" class in a ``unittest.TestCase``::

        class TestSomething(fakeable.FakeableCleanupMixin, unittest.TestCase):
            def test(self):
                fakeable.set_fake_class("Something", FakeSomething)
                self.assertTrue(do_something())

    Before the method ``test()`` is executed the ``setUp()`` method will invoke
    :func:`fakeable.clear` to make sure there are no leftover fakes that were
    registered elsewhere.  Also, after the ``test()`` method completes,
    ``tearDown()`` will invoke  :func:`fakeable.clear` to make sure that none
    of the registered fakes are left behind to screw things up downstream.

    Note, however, that ``fakeable.FakeableCleanupMixin``
    *must* occur before ``unittest.TestCase`` in the base class list.
    Otherwise, the ``setUp()`` and ``tearDown()`` methods of
    ``FakeableCleanupMixin`` will not be invoked.

    *Bad Example (of specifying base classes of a test case)*::

        # BAD!! -- because unittest.TestCase is specified *before*
        # fakeable.FakeableCleanupMixin in the base class list,
        # the setUp() and tearDown() methods of FakeableCleanupMixin will not
        # be invoked, defeating the purpose of adding it as a base class
        class TestSomething(unittest.TestCase, fakeable.FakeableCleanupMixin):
            ...

    *Good Example (of specifying base classes of a test case)*::

        # GOOD -- because unittest.TestCase is specified *after*
        # fakeable.FakeableCleanupMixin in the base class list,
        # the setUp() and tearDown() methods of FakeableCleanupMixin *will*
        # be invoked, properly unregistering all registered fakes
        class TestSomething(fakeable.FakeableCleanupMixin, unittest.TestCase):
            ...

    If the ``FakeableCleanupMixin`` subclass also wants to override ``setUp()``
    and/or ``tearDown()``, be sure to use the ``super()`` built-in to call the
    method of the same name in the superclass (as opposed to naming the
    superclass and calling it directly).  Using ``super()`` ensures that the
    method-resolution order ("mro") will be used and each superclass' method
    will be invoked in the correct order.

    *Bad Example (of overriding the setUp() method)*::

        class TestSomething(fakeable.FakeableCleanupMixin, unittest.TestCase):
            def setUp(self):
                # BAD!! -- does not respect the MRO and some superclass setUp()
                # methods may not be invoked
                fakeable.FakeableCleanupMixin.setUp(self)
                ...

    *Good Example (of overriding the setUp() method)*::

        class TestSomething(fakeable.FakeableCleanupMixin, unittest.TestCase):
            def setUp(self):
                # GOOD -- respects the MRO and ensures that the setUp() method
                # of each superclass is invoked and in the correct order
                super(TestSomething, self).setUp()
                ...
    """

    def setUp(self):
        """
        Invokes the ``setUp`` method of the superclass, and then
        :func:`fakeable.clear`.
        This ensures that fakes that have been previously set do not leak into
        tests.
        """
        super(FakeableCleanupMixin, self).setUp()
        clear()

    def tearDown(self):
        """
        Invokes :func:`fakeable.clear` and then the ``tearDown()`` method of
        the superclass.
        This ensures that fakes that have been set in tests do not leak into
        other tests.  It also precludes the need to explicitly unregister
        fake objects.
        """
        try:
            clear()
        finally:
            super(FakeableCleanupMixin, self).tearDown()
