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

"""
Provides a mechanism by which classes can produce "fake" instances during unit
tests and real instances when not under test.
"""

from __future__ import print_function
from __future__ import unicode_literals

__all__ = [
    "Fakeable",
    "set_fake_class",
    "set_fake_object",
    "unset",
    "clear",
    "add_created_callback",
    "remove_created_callback",
    "FakeableCleanupMixin",
]

__version__ = "1.0.3"


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

    def __new__(mcs, name, bases, dict_):
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
        type_ = type.__new__(mcs, name, bases, dict_)
        return type_

    def __call__(cls, *args, **kwargs):
        fake_name = cls.__FAKE_NAME__

        # try looking up the fake object by the class first
        try:
            instance = FAKE_FACTORY.get(cls, *args, **kwargs)
        except FAKE_FACTORY.FakeNotFound:
            pass
        else:
            FAKE_FACTORY.notify_fakeable_created(fake_name, instance, cls)
            return instance

        # try looking up the fake object by name
        try:
            instance = FAKE_FACTORY.get(fake_name, *args, **kwargs)
        except FAKE_FACTORY.FakeNotFound:
            pass
        else:
            FAKE_FACTORY.notify_fakeable_created(fake_name, instance, cls)
            return instance

        # no fake instance was registered; create a real instance
        instance = type.__call__(cls, *args, **kwargs)
        FAKE_FACTORY.notify_fakeable_created(fake_name, instance, cls)
        return instance


class FakeFactory(object):
    """
    A database of fake objects.
    """

    def __init__(self):
        self.fake_factories = {}
        self.fakeable_created_callbacks = []

    def set_fake_class(self, name, value):
        """
        See module-level set_fake_class() function for full documentation
        """
        entry = FakeClassEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def set_fake_object(self, name, value):
        """
        See module-level set_fake_object() function for full documentation
        """
        entry = FakeObjectEntry(self, name, value)
        self.fake_factories[name] = entry
        return entry

    def unset(self, name):
        """
        See module-level unset() function for full documentation
        """
        try:
            del self.fake_factories[name]
        except KeyError:
            return False
        else:
            return True

    def clear(self):
        """
        See module-level clear() function for full documentation
        """
        self.fake_factories.clear()
        self.fakeable_created_callbacks = []

    def add_created_callback(self, callback):
        """
        See module-level add_created_callback() function
        for full documentation
        """
        self.fakeable_created_callbacks.append(callback)

    def remove_created_callback(self, callback):
        """
        See module-level remove_created_callback() function
        for full documentation
        """
        try:
            self.fakeable_created_callbacks.remove(callback)
        except ValueError:
            return False
        else:
            return True

    def notify_fakeable_created(self, name, obj, obj_type):
        """
        Notifies all callbacks about an instance of a fakeable class being
        created.  This method is not normally invoked directly, but rather is
        invoked by the :class:`~fakeable.Fakeable` metaclass when it is
        requested to create a new object.

        The arguments are exactly those to specify to the callbacks registered
        via :meth:`add_created_callback` so see the documentation for that
        method for details.
        """
        for callback in self.fakeable_created_callbacks:
            callback(name, obj, obj_type)

    def get(self, name, *args, **kwargs):
        """
        Gets or creates the fake object for a class.

        This method is the one used by the :class:`fakeable.Fakeable` metaclass
        to create the fake instances.  It should not normally be invoked
        directly.

        Arguments:
            *name* (string or :class:`fakeable.Fakeable` instance)
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
        """
        Invokes self.fake_factory.unset(self.name).
        """
        self.fake_factory.unset(self.name)

    def get(self, *args, **kwargs):
        """
        Must be implemented by subclasses to get or create the fake object.
        The given arguments are those that were specified to the class
        constructor.
        """
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
FAKE_FACTORY = FakeFactory()


def set_fake_class(name, value):
    """
    Configures the class with the given name to create fake objects instead
    of real objects when created.  When an instance of the class of the
    given name is created a new instance of the given type will be created
    instead.

    Arguments:
        *name* (string or :class:`fakeable.Fakeable`)
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
    FAKE_FACTORY.set_fake_class(name, value)


def set_fake_object(name, value):
    """
    Configures the class with the given name to always use a fake object
    instead of real objects when created.  When an instance of the class of
    the given name is created the given value will be returned instead.

    Arguments:
        *name* (string or :class:`fakeable.Fakeable`)
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
    FAKE_FACTORY.set_fake_object(name, value)


def unset(name):
    """
    Unregisters a fake that was registered by a previous invocation of
    set_fake_object() or set_fake_class().

    Arguments:
        *name* (string or :class:`fakeable.Fakeable`)
            the name of the class, or the class itself, whose fake is to be
            unregistered; if a string, this will be the name of the class
            or, if the class defines __FAKE_NAME__, the value of that class'
            __FAKE_NAME__ attribute.

    Returns True if a fake was indeed registered with the given name and
    was successfully unregistered.  Returns False if a fake was *not*
    registered with the given name and therefore this function did nothing.
    """
    FAKE_FACTORY.unset(name)


def add_created_callback(callback):
    """
    Registers a callback to be invoked each time an instance of a
    :class:`~fakeable.Fakeable` class is created.  The given callback will
    invoked each time that a class with the :class:`~fakeable.Fakeable`
    metaclass is created, whether it returns a fake object or a new instance of
    the real class.  This can be useful during unit testing to examine the
    objects created by a third-party after the fact.

    No checking for duplicate callback registrations is performed; therefore,
    if a given callback is registered twice then it will be invoked twice each
    time that an instance of a :class:`~fakeable.Fakeable` class is created.

    Callbacks are invoked synchronously, and in the order in which they are
    added.  No exception handling is performed around the callbacks; therefore,
    if a callback raises an exception it will trickle up the call stack until
    it is either caught or falls of the end, aborting the program.  This will
    also prevent the other callbacks from receiving the notification.

    Callbacks may be unregistered by
    :func:`~fakeable.remove_created_callback`
    (to unregister a specific callback)
    or :func:`~fakeable.clear` (to unregister *all* callbacks).

    Arguments:
        *callback* (function)
            a function that will be invoked each time an instance of a
            :class:`fakeable.Fakeable` class is created; this function must
            accept the arguments documented below.

    The arguments of the callback function are:
        *name* (string)
            the name of the fakeable type, which is normally a string, and will
            be equal to the ``__FAKE_NAME__`` attribute of the
            :class:`~fakeable.Fakeable` class.
        *obj* (an object)
            the object that was returned by the request for a new instance of
            the :class:`~fakeable.Fakeable` class; this will be a new instance
            of the :class:`~fakeable.Fakeable` class if no fake object is
            registered or the fake object if one is.
        *obj_type* (class object)
            the class object of the :class:`~fakeable.Fakeable` class.
    """
    FAKE_FACTORY.add_created_callback(callback)


def remove_created_callback(callback):
    """
    Unregisters a callback that was registered by a previous invocation of
    :func:`~fakeable.add_created_callback`.
    If the given callback is registered more than once then only one of its
    registrations will be removed.  Therefore, to fully unregister a callback
    there must be one call to this function for each call to
    :func:`~fakeable.add_created_callback`.

    Arguments:
        *callback* (function)
            the callback to remove; this must be the exact object that was
            specified to add_fake_created_callback() for the "callback"
            argument

    Returns True if the given callback was found in the list of registered
    callbacks and was removed; returns False if the given callback was *not*
    found in the list of registered callbacks and therefore this method did
    nothing.
    """
    return FAKE_FACTORY.remove_created_callback(callback)


def clear():
    """
    Unregisters all fake objects that have been previously registered
    and all callbacks that have been registered via add_created_callback().
    """
    FAKE_FACTORY.clear()


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
