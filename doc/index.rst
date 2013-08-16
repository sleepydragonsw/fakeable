.. Fakeable documentation master file, created by
   sphinx-quickstart on Tue Aug 13 21:07:31 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Fakeable - Transparently Use Fake Objects in Unit Tests
=======================================================

.. moduleauthor:: Denver Coneybeare

*Fakeable* is a Python library that allows seamlessly replacing "real" objects
with "fake" objects during unit testing.
"Faking out" objects is a generally-accepted practice in unit testing
to make it easy to traverse every code path of a method or function
without having to set up a real environment to make that happen.
*Fakeable* works at the *class* level
and any class that wants to be fakeable during unit tests
need only add a single line to its class definition to make this dream a reality.

*Fakeable* is supported in Python 2.7 and Python 3.3,
and also has been confirmed to work in PyPy 2.1 and PyPy3 2.1-beta1.

*Fakeable* is free and open-source software,
released under the Apache License Version 2.0.

Simple Example
==============

This section shows a simple, contrived example of how *Fakeable* can be used
to test otherwise difficult to create scenarios.

Suppose you have a class named ``HttpDownloader``
that downloads files from the Internet using the HTTP protocol::

    import urllib2
    class HttpDownloader(object):
        # download the contents of the given URL and return it;
        # return None if the given URL is invalid
        def download(self, url):
            try:
                f = urllib2.urlopen(url)
            except urllib2.URLError:
                return None
            else:
                data = f.read()
                f.close()
                return data

Now suppose that you want to test another function called ``download_urls()``
that uses ``HttpDownloader`` in its implementation::

    def download_urls(urls):
        downloader = HttpDownloader()
        datas = []
        for url in urls:
            data = downloader.download(url)
            datas.append(data)
        return datas

In order to test this function properly
you would have to start a real HTTP server, presumaby on localhost,
and have it return some pre-canned responses.
This seems reasonable.

But what about testing the error conditions?
What would you specify for an invalid URL?
A bit of experimentation would give some good sample data
but there is no guarantee that the same failures would occur
on another computer, another operating system, or another Python implementation.
This is where faking comes in handy.

Let's create a fake version of ``HttpDownloader``
that simply returns None, simulating the URLError being handled::

    class FakeHttpDownloader(object):
        def download(self, url):
            return None

Next, make the *real* ``HttpDownloader`` class fakeable::

    import fakeable
    import urllib2
    class HttpDownloader(object):
        __metaclass__ = fakeable.Fakeable
        def download(self, url):
            ...

Finally, write the unit test that uses the fake version of ``HttpDownloader``::

    import unittest
    class TestHttpDownloader(unittest.TestCase):
        def test_InvalidUrl(self):
            with fakeable.set_fake_class("HttpDownloader", FakeHttpDownloader):
                retval = download_urls(["foo", "bar"])
            self.assertListEqual(retval, [None, None])

This unit test can be further simplified
by using the :class:`~fakeable.FakeableCleanupMixin`
to automatically unregister the fakes::

    import unittest
    class TestHttpDownloader(unittest.TestCase, fakeable.FakeableCleanupMixin):
        def test_InvalidUrl(self):
            fakeable.set_fake_class("HttpDownloader", FakeHttpDownloader)
            retval = download_urls(["foo", "bar"])
            self.assertListEqual(retval, [None, None])

Usage
=====

Making Classes Fakeable
-----------------------

In order for a class to be Fakeable, it must opt-in to this functionality
by declaring :class:`fakeable.Fakeable` as the metaclass.
See the documentation for :class:`fakeable.Fakeable`
for details on how to declare a metaclass (it's easy!).
The "magic" of the metaclass is that before a new object of the class is created
it first checks to see if a fake version has been registered;
if a fake is found then it is returned instead of a new instance of the class;
otherwise, a new instance of the class is created and returned as per usual.

Registering Fake Objects
------------------------

When unit testing, a class can be replaced with a fake version
by setting either an object or a class to be the fake replacement.

If an object is specified, via :func:`fakeable.set_fake_object`,
then each time an instance of the fakeable class is created
the registered object will be returned instead.

If a class is specified, via :func:`fakeable.set_fake_class`,
then each time an instance of the fakeable class is requested
a new instance of the *fake* class will be created and returned instead.
Note that any arguments that would have otherwise been specified to the
``__init__()`` method of the fakeable class
will be specified to the ``__init__()`` method of the fake class.
This means that either the fake class' ``__init__()`` method
must have the same argument list as the real class
or use "catch-all" arguments, such as ``__init__(self, *args, **kwargs)``.

If a fake object and a fake class are both registered for a particular class
then the most-recently-registered one will be used.
Each time a fake object or fake class is registered,
it replaces any previously-registered fake classes or objects.

Fakeable Class Names
--------------------

When a fake object is registered via :func:`fakeable.set_fake_object`
or a fake class is registered via :func:`fakeable.set_fake_class`
a *name* for the fake class must be specified.

By default, this name is a string whose value is the name of the class
that is desired to be faked.
For example, to use a fake version of the ``HttpDownloader`` class,
specify the name ``"HttpDownloader"``.
A fakeable class can override this default name
by setting ``__FAKE_NAME__`` in its class definition.
If a class overrides the default fake name, then that value must be used
instead of the default value.
A class' fake name, either the default value or overrided value,
is always available via the ``__FAKE_NAME__`` attribute of the class.
For example, to discover the name to use when faking out the ``HttpDownloader`` class
check the value of ``HttpDownloader.__FAKE_NAME__``.
Although ``__FAKE_NAME__`` is normally a string object,
it may technically be any hashable object, including ``int``, ``float``, and ``frozenset``.

If two different classes happen to have the same name,
the name can instead be the class object of the real class itself.
For example, to use a fake version of the ``HttpDownloader`` class,
specify the name as the ``HttpDownloader`` class.

If both the fakeable class' name and class object are registered
then the object or class registered with the *class* object will be used.
This is because the :class:`fakeable.Fakeable` class
first checks to see if there is a fake registered against the *class* object.
Only if no fake registered against the fakeable class
does it check to see if one is registered against the *name* of the fakeable class.

The author of *Fakeable* generally recommends to use string names whenever possible.
The reason is that this removes the need to import the real class
in the unit tests, only to replace it with fake versions.
That being said, using the class objects of the fakeable classes as names
gives a degree of "type safety", in that if the fakeable class is
renamed, moved, or deleted an exception will be raised when the tests are run,
pointing to tests that needs to be updated.
No such error reporting occurs when string names are used.
In the end, both facilities work equally well
and it is up to the test author to choose which method is preferred.

Unregistering Fake Objects
--------------------------

There are three different ways to unregister a fake object:

1. :func:`fakeable.unset`
2. :func:`fakeable.clear`
3. the context manager returned from :func:`fakeable.set_fake_object`
   or :func:`fakeable.set_fake_class`
4. :class:`~fakeable.FakeableCleanupMixin`

By invoking :func:`fakeable.unset` with the same ``name``
that was specified to either :func:`fakeable.set_fake_object`
or :func:`fakeable.set_fake_class`
it will cause the *real* class to once again produce *real* objects.
It is good practice to perform a matching "unset" for each "set"
to avoid using fake objects outside of the intended scope.

By invoking :func:`fakeable.clear` all registered fakes will be unregistered.
This is equivalent to invoking :func:`fakeable.unset` for each registered fake.
If using the built-in ``unittest`` module,
it is a good idea to call :func:`fakeable.clear` in both ``setUp()`` and ``tearDown()``
to ensure a pristine fake environment
and that no fake objects "leak" outside the unit test, respectively.

Both :func:`fakeable.set_fake_object` and :func:`fakeable.set_fake_class`
return a *context manager*, which can be used in a *with* statement
to automatically unregister the fake.
For example::

    with fakeable.set_fake_object("Number", 1):
        ...

In the code sample above, the fake object will be automatically unset
when the "with" block is exited.

If using the ``unittest`` testing framework from the Python standard library
you can use the :class:`~fakeable.FakeableCleanupMixin` class
to automatically unregister all fakes at the beginning and end of each test case.
This is especially useful to avoid fakes accidentally remaining registered
after the test completes.
To use :class:`~fakeable.FakeableCleanupMixin`,
simply make your unit test case classes inherit from both
``unittest.TestCase`` and :class:`~fakeable.FakeableCleanupMixin`.
This will add ``setUp()`` and ``tearDown`` methods to the test class
which invoke :func:`fakeable.clear` before and after your test, respectively.
See the documentation for :class:`~fakeable.FakeableCleanupMixin` for details.

API Reference
=============

The ``Fakeable`` Metaclass
--------------------------

.. autoclass:: fakeable.Fakeable

Registering and Unregistering Fakes
-----------------------------------

.. autofunction:: fakeable.set_fake_class
.. autofunction:: fakeable.set_fake_object
.. autofunction:: fakeable.unset
.. autofunction:: fakeable.clear

The ``FakeableCleanupMixin`` Helper Class
-----------------------------------------

.. autoclass:: fakeable.FakeableCleanupMixin
   :members:

License
=======

*Fakeable* is free and open-source software,
released under the Apache License version 2.0.
The text of the license is available in the file named ``LICENSE.txt``
in the source distribution
and is also available on the Internet at
http://www.apache.org/licenses/LICENSE-2.0.html

Bug Reports and Feature Requests
================================
Please report issues and feature requests on the GitHub issue tracker:
https://github.com/sleepydragonsw/fakeable/issues.

Alternately, fork the repository on GitHub and issue a pull request.

Contact Information
===================

*Fakeable* was written and is maintained by Denver Coneybeare.
Version 1.0.0 was released in August 2013.
Denver can be contacted at denver@sleepydragon.org.

The source code for *Fakeable* is freely available at
https://github.com/sleepydragonsw/fakeable.

The documentation for *Fakeable* is published at
https://fakeable.readthedocs.org

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
