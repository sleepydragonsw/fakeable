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
