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

Being Notified When Fakeable Objects Are Created
------------------------------------------------

.. autofunction:: fakeable.add_created_callback
.. autofunction:: fakeable.remove_created_callback

The ``FakeableCleanupMixin`` Helper Class
-----------------------------------------

.. autoclass:: fakeable.FakeableCleanupMixin
   :members:
