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

Contents
========

.. toctree::
   :maxdepth: 2

   example
   usage
   api

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

License
=======

*Fakeable* is free and open-source software,
released under the Apache License version 2.0.
The text of the license is available in the file named ``LICENSE.txt``
in the source distribution
and is also available on the Internet at
http://www.apache.org/licenses/LICENSE-2.0.html

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
