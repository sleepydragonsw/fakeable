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

import fakeable

import unittest

import six


class MyCoolClass(six.with_metaclass(fakeable.Fakeable)):
    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class MyUnfakeableClass(object):
    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class MyUnfakeableClass1(object):
    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class MyUnfakeableClass2(object):
    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class MyCoolClassCustomFakeName(six.with_metaclass(fakeable.Fakeable)):
    __FAKE_NAME__ = "CustomName"

    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2


class FakeCreatedCallbackTester(object):
    """
    An object that can be specified to add_created_callback() to
    test that the expected invocations do (or do not) occur.
    """

    NEXT_INDEX = 0

    def __init__(self, test):
        self.test = test
        self.invocations = []

    def __call__(self, name, obj, obj_type):
        index = type(self).NEXT_INDEX
        type(self).NEXT_INDEX += 1
        invocation = self.Invocation(index, name, obj, obj_type)
        self.invocations.append(invocation)

    def assert_invoked_exactly_once(self):
        num_invocations = len(self.invocations)
        if num_invocations == 0:
            self.test.fail(
                "callback was not invoked, but expected exactly 1 invocation")
        elif num_invocations > 1:
            self.test.fail(
                "callback was not invoked {} times, but expected exactly "
                "1 invocation".format(num_invocations))
        invocation = self.invocations[0]
        return invocation

    def assert_invocation_count(self, expected_count):
        num_invocations = len(self.invocations)
        if num_invocations != expected_count:
            self.test.fail(
                "callback was not invoked {} times, but expected exactly {} "
                "invocations".format(num_invocations, expected_count))
        return self.invocations[:expected_count]

    class Invocation(object):
        def __init__(self, index, name, obj, obj_type):
            self.index = index
            self.name = name
            self.obj = obj
            self.obj_type = obj_type


class Test_Fakeable___new__(fakeable.FakeableCleanupMixin, unittest.TestCase):

    def test_DefaultFakeName(self):
        self.assertEqual(MyCoolClass.__FAKE_NAME__, "MyCoolClass")

    def test_CustomFakeName(self):
        self.assertEqual(MyCoolClassCustomFakeName.__FAKE_NAME__, "CustomName")

    def test_CustomFakeNameNotHashable(self):
        with self.assertRaises(TypeError):
            class NameNotHashable(six.with_metaclass(fakeable.Fakeable)):
                __FAKE_NAME__ = set()


class Test_Fakeable___call__(fakeable.FakeableCleanupMixin, unittest.TestCase):

    def test_NoFakeRegistered(self):
        x = MyCoolClass()
        self.assertIsInstance(x, MyCoolClass)

    def test_NoFakeRegistered_PositionalArgs(self):
        x = MyCoolClass(1, 2)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_NoFakeRegistered_KeywordArgs(self):
        x = MyCoolClass(arg1=1, arg2=2)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_FakeObjectRegisteredByName(self):
        fake_object = object()
        fakeable.set_fake_object("MyCoolClass", fake_object)
        x = MyCoolClass()
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByName_PositionalArgs(self):
        fake_object = object()
        fakeable.set_fake_object("MyCoolClass", fake_object)
        x = MyCoolClass(1, 2)
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByName_KeywordArgs(self):
        fake_object = object()
        fakeable.set_fake_object("MyCoolClass", fake_object)
        x = MyCoolClass(arg1=1, arg2=2)
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByClass(self):
        fake_object = object()
        fakeable.set_fake_object(MyCoolClass, fake_object)
        x = MyCoolClass()
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByClass_PositionalArgs(self):
        fake_object = object()
        fakeable.set_fake_object(MyCoolClass, fake_object)
        x = MyCoolClass(1, 2)
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByClass_KeywordArgs(self):
        fake_object = object()
        fakeable.set_fake_object(MyCoolClass, fake_object)
        x = MyCoolClass(arg1=1, arg2=2)
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByCustomName(self):
        fake_object = object()
        fakeable.set_fake_object("CustomName", fake_object)
        x = MyCoolClassCustomFakeName()
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByCustomName_PositionalArgs(self):
        fake_object = object()
        fakeable.set_fake_object("CustomName", fake_object)
        x = MyCoolClassCustomFakeName(1, 2)
        self.assertIs(x, fake_object)

    def test_FakeObjectRegisteredByCustomName_KeywordArgs(self):
        fake_object = object()
        fakeable.set_fake_object("CustomName", fake_object)
        x = MyCoolClassCustomFakeName(arg1=1, arg2=2)
        self.assertIs(x, fake_object)

    def test_2FakeObjectsRegisteredByName_OtherNameRegisteredAfter(self):
        fake_object1 = object()
        fake_object2 = object()
        fakeable.set_fake_object("MyCoolClass", fake_object1)
        fakeable.set_fake_object("SomeOtherClass", fake_object2)
        x = MyCoolClass()
        self.assertIs(x, fake_object1)

    def test_2FakeObjectsRegisteredByName_OtherNameRegisteredBefore(self):
        fake_object1 = object()
        fake_object2 = object()
        fakeable.set_fake_object("SomeOtherClass", fake_object1)
        fakeable.set_fake_object("MyCoolClass", fake_object2)
        x = MyCoolClass()
        self.assertIs(x, fake_object2)

    def test_FakeObjectRegisteredTwiceByName(self):
        fake_object1 = object()
        fake_object2 = object()
        fakeable.set_fake_object("MyCoolClass", fake_object1)
        fakeable.set_fake_object("MyCoolClass", fake_object2)
        x = MyCoolClass()
        self.assertIs(x, fake_object2)

    def test_FakeObjectRegisteredByNameAndClass_NameRegisteredFirst(self):
        fake_object1 = object()
        fake_object2 = object()
        fakeable.set_fake_object("MyCoolClass", fake_object1)
        fakeable.set_fake_object(MyCoolClass, fake_object2)
        x = MyCoolClass()
        self.assertIs(x, fake_object2)

    def test_FakeObjectRegisteredByNameAndClass_NameRegisteredAfter(self):
        fake_object1 = object()
        fake_object2 = object()
        fakeable.set_fake_object(MyCoolClass, fake_object1)
        fakeable.set_fake_object("MyCoolClass", fake_object2)
        x = MyCoolClass()
        self.assertIs(x, fake_object1)

    def test_FakeClassRegisteredByName(self):
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass)

    def test_FakeClassRegisteredByName_PositionalArgs(self):
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass)
        x = MyCoolClass(1, 2)
        self.assertIsInstance(x, MyUnfakeableClass)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_FakeClassRegisteredByName_KeywordArgs(self):
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass)
        x = MyCoolClass(arg1=1, arg2=2)
        self.assertIsInstance(x, MyUnfakeableClass)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_FakeClassRegisteredByClass(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass)

    def test_FakeClassRegisteredByClass_PositionalArgs(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass)
        x = MyCoolClass(1, 2)
        self.assertIsInstance(x, MyUnfakeableClass)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_FakeClassRegisteredByClass_KeywordArgs(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass)
        x = MyCoolClass(arg1=1, arg2=2)
        self.assertIsInstance(x, MyUnfakeableClass)
        self.assertEqual(x.arg1, 1)
        self.assertEqual(x.arg2, 2)

    def test_2FakeClassesRegisteredByClass_OtherClassRegisteredAfter(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass1)
        fakeable.set_fake_class(MyCoolClassCustomFakeName, MyUnfakeableClass2)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass1)

    def test_2FakeClassesRegisteredByClass_OtherClassRegisteredBefore(self):
        fakeable.set_fake_class(MyCoolClassCustomFakeName, MyUnfakeableClass1)
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass2)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass2)

    def test_FakeClassRegisteredTwiceByClass(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass1)
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass2)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass2)

    def test_ClassRegisteredByNameAndClass_NameRegisteredFirst(self):
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass1)
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass2)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass2)

    def test_ClassRegisteredByNameAndClass_NameRegisteredAfter(self):
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass1)
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass2)
        x = MyCoolClass()
        self.assertIsInstance(x, MyUnfakeableClass1)


class Test_FakeableCleanupMixin(unittest.TestCase):

    def test_setUp_SuperclassSetUpSuccessful(self):
        fakeable.set_fake_object("MyCoolClass", object())
        x = self.TestableFakeableCleanupMixin()
        x.setUp()
        obj = MyCoolClass()
        self.assertIsInstance(
            obj, MyCoolClass, "setUp() should have cleared all of the "
            "registered fakes")
        self.assertTrue(x.setUp_invoked)

    def test_setUp_SuperclassSetUpRaisesException(self):
        fake_my_cool_class_instance = object()
        fakeable.set_fake_object("MyCoolClass", fake_my_cool_class_instance)
        x = self.TestableFakeableCleanupMixin(setUp_exception=ValueError())
        with self.assertRaises(ValueError):
            x.setUp()
        obj = MyCoolClass()
        self.assertIs(
            obj, fake_my_cool_class_instance, "setUp() should *not* have "
            "cleared all of the registered fakes")
        self.assertTrue(x.setUp_invoked)

    def test_tearDown_SuperclassSetUpSuccessful(self):
        fakeable.set_fake_object("MyCoolClass", object())
        x = self.TestableFakeableCleanupMixin()
        x.tearDown()
        obj = MyCoolClass()
        self.assertIsInstance(
            obj, MyCoolClass, "tearDown() should have cleared all of the "
            "registered fakes")
        self.assertTrue(x.tearDown_invoked)

    def test_tearDown_SuperclassSetUpRaisesException(self):
        fakeable.set_fake_object("MyCoolClass", object())
        x = self.TestableFakeableCleanupMixin(tearDown_exception=ValueError())
        with self.assertRaises(ValueError):
            x.tearDown()
        obj = MyCoolClass()
        self.assertIsInstance(
            obj, MyCoolClass, "tearDown() should have cleared all of the "
            "registered fakes")
        self.assertTrue(x.tearDown_invoked)

    class DemoBaseClass(object):
        def __init__(self, setUp_exception=None, tearDown_exception=None):
            self.setUp_exception = setUp_exception
            self.tearDown_exception = tearDown_exception
            self.setUp_invoked = False
            self.tearDown_invoked = False

        def setUp(self):
            self.setUp_invoked = True
            if self.setUp_exception is not None:
                raise self.setUp_exception

        def tearDown(self):
            self.tearDown_invoked = True
            if self.tearDown_exception is not None:
                raise self.tearDown_exception

    class TestableFakeableCleanupMixin(
            fakeable.FakeableCleanupMixin, DemoBaseClass):
        pass


class Test_add_created_callback(
        fakeable.FakeableCleanupMixin, unittest.TestCase):

    def test_NoFakeRegistered_DefaultFakeName(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        MyCoolClass()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "MyCoolClass")
        self.assertIsInstance(invocation.obj, MyCoolClass)
        self.assertIs(invocation.obj_type, MyCoolClass)

    def test_NoFakeRegistered_CustomFakeName(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        MyCoolClassCustomFakeName()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "CustomName")
        self.assertIsInstance(invocation.obj, MyCoolClassCustomFakeName)
        self.assertIs(invocation.obj_type, MyCoolClassCustomFakeName)

    def test_2FakeableInstancesCreated(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        MyCoolClass()
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIsInstance(invocations[0].obj, MyCoolClass)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIsInstance(invocations[1].obj, MyCoolClass)
        self.assertIs(invocations[1].obj_type, MyCoolClass)

    def test_2CallbacksRegistered(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        MyCoolClass()
        invocation1 = callback1.assert_invoked_exactly_once()
        self.assertEqual(invocation1.name, "MyCoolClass")
        self.assertIsInstance(invocation1.obj, MyCoolClass)
        self.assertIs(invocation1.obj_type, MyCoolClass)
        invocation2 = callback2.assert_invoked_exactly_once()
        self.assertIs(invocation2.name, invocation1.name)
        self.assertIs(invocation2.obj, invocation1.obj)
        self.assertIs(invocation2.obj_type, invocation1.obj_type)

    def test_2CallbacksRegistered_InvokedInCorrectOrder(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        MyCoolClass()
        invocation1 = callback1.assert_invoked_exactly_once()
        invocation2 = callback2.assert_invoked_exactly_once()
        self.assertLess(invocation1.index, invocation2.index)

    def test_CallbackRegisteredTwice(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.add_created_callback(callback)
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIsInstance(invocations[0].obj, MyCoolClass)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIsInstance(invocations[1].obj, MyCoolClass)
        self.assertIs(invocations[1].obj_type, MyCoolClass)

    def test_FakeObjectRegisteredByName(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fake_object = object()
        fakeable.set_fake_object("MyCoolClass", fake_object)
        MyCoolClass()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "MyCoolClass")
        self.assertIs(invocation.obj, fake_object)
        self.assertIs(invocation.obj_type, MyCoolClass)

    def test_FakeObjectRegisteredByName_2InstancesCreated(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fake_object = object()
        fakeable.set_fake_object("MyCoolClass", fake_object)
        MyCoolClass()
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIs(invocations[0].obj, fake_object)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIs(invocations[1].obj, fake_object)
        self.assertIs(invocations[1].obj_type, MyCoolClass)

    def test_FakeObjectRegisteredByClass(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fake_object = object()
        fakeable.set_fake_object(MyCoolClass, fake_object)
        MyCoolClass()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "MyCoolClass")
        self.assertIs(invocation.obj, fake_object)
        self.assertIs(invocation.obj_type, MyCoolClass)

    def test_FakeObjectRegisteredByClass_2InstancesCreated(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fake_object = object()
        fakeable.set_fake_object(MyCoolClass, fake_object)
        MyCoolClass()
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIs(invocations[0].obj, fake_object)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIs(invocations[1].obj, fake_object)
        self.assertIs(invocations[1].obj_type, MyCoolClass)

    def test_FakeClassRegisteredByName(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass)
        MyCoolClass()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "MyCoolClass")
        self.assertIsInstance(invocation.obj, MyUnfakeableClass)
        self.assertIs(invocation.obj_type, MyCoolClass)

    def test_FakeClassRegisteredByName_2InstancesCreated(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.set_fake_class("MyCoolClass", MyUnfakeableClass)
        MyCoolClass()
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIsInstance(invocations[0].obj, MyUnfakeableClass)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIsInstance(invocations[1].obj, MyUnfakeableClass)
        self.assertIs(invocations[1].obj_type, MyCoolClass)
        self.assertIsNot(invocations[0].obj, invocations[1].obj)

    def test_FakeClassRegisteredByClass(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass)
        MyCoolClass()
        invocation = callback.assert_invoked_exactly_once()
        self.assertEqual(invocation.name, "MyCoolClass")
        self.assertIsInstance(invocation.obj, MyUnfakeableClass)
        self.assertIs(invocation.obj_type, MyCoolClass)

    def test_FakeClassRegisteredByClass_2InstancesCreated(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.set_fake_class(MyCoolClass, MyUnfakeableClass)
        MyCoolClass()
        MyCoolClass()
        invocations = callback.assert_invocation_count(2)
        self.assertEqual(invocations[0].name, "MyCoolClass")
        self.assertIsInstance(invocations[0].obj, MyUnfakeableClass)
        self.assertIs(invocations[0].obj_type, MyCoolClass)
        self.assertEqual(invocations[1].name, "MyCoolClass")
        self.assertIsInstance(invocations[1].obj, MyUnfakeableClass)
        self.assertIs(invocations[1].obj_type, MyCoolClass)


class Test_remove_created_callback(
        fakeable.FakeableCleanupMixin, unittest.TestCase):

    def test_0CallbacksAdded_RemoveNeverAddedCallback(self):
        callback = FakeCreatedCallbackTester(self)
        retval = fakeable.remove_created_callback(callback)
        self.assertIs(retval, False)
        fakeable.add_created_callback(callback)
        MyCoolClass()
        callback.assert_invoked_exactly_once()

    def test_1CallbacksAdded_RemoveNeverAddedCallback(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        retval = fakeable.remove_created_callback(object())
        self.assertIs(retval, False)
        MyCoolClass()
        callback.assert_invoked_exactly_once()

    def test_1CallbacksAdded_RemoveTheAddedCallback(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        retval = fakeable.remove_created_callback(callback)
        self.assertIs(retval, True)
        MyCoolClass()
        callback.assert_invocation_count(0)

    def test_2CallbacksAdded_RemoveNeverAddedCallback(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        retval = fakeable.remove_created_callback(object())
        self.assertIs(retval, False)
        MyCoolClass()
        callback1.assert_invoked_exactly_once()
        callback2.assert_invoked_exactly_once()

    def test_2CallbacksAdded_Remove1stAddedCallback(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        retval = fakeable.remove_created_callback(callback1)
        self.assertIs(retval, True)
        MyCoolClass()
        callback1.assert_invocation_count(0)
        callback2.assert_invoked_exactly_once()

    def test_2CallbacksAdded_Remove2ndAddedCallback(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        retval = fakeable.remove_created_callback(callback2)
        self.assertIs(retval, True)
        MyCoolClass()
        callback1.assert_invoked_exactly_once()
        callback2.assert_invocation_count(0)

    def test_2CallbacksAdded_RemoveBothAddedCallbacks(self):
        callback1 = FakeCreatedCallbackTester(self)
        callback2 = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback1)
        fakeable.add_created_callback(callback2)
        retval1 = fakeable.remove_created_callback(callback1)
        self.assertIs(retval1, True)
        retval2 = fakeable.remove_created_callback(callback2)
        self.assertIs(retval2, True)
        MyCoolClass()
        callback1.assert_invocation_count(0)
        callback2.assert_invocation_count(0)

    def test_1CallbacksAdded2Times_RemoveTheAddedCallback1Time(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.add_created_callback(callback)
        retval = fakeable.remove_created_callback(callback)
        self.assertIs(retval, True)
        MyCoolClass()
        callback.assert_invoked_exactly_once()

    def test_1CallbacksAdded2Times_RemoveTheAddedCallback2Times(self):
        callback = FakeCreatedCallbackTester(self)
        fakeable.add_created_callback(callback)
        fakeable.add_created_callback(callback)
        retval1 = fakeable.remove_created_callback(callback)
        self.assertIs(retval1, True)
        retval2 = fakeable.remove_created_callback(callback)
        self.assertIs(retval2, True)
        MyCoolClass()
        callback.assert_invocation_count(0)


if __name__ == "__main__":
    unittest.main()
