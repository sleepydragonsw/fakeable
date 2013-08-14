fakeable
By: Denver Coneybeare <denver@sleepydragon.org>
Aug 12, 2013

Fakeable is a Python library that provides a facility for transparently
replacing objects with fake versions during unit testing.  The main advantage
of Fakeable is that from the point of view of the production code there is
nothing that needs to be done except to declare a specific metaclass to opt-in
to being faked.  Then, during testing the tests specify to use a fake version
of a specific class and then "magically" at runtime a fake version is used.

Full documentation available at: https://fakeable.readthedocs.org
Source code available at: https://github.com/sleepydragonsw/fakeable

For example, consider the class below, which simply reads the contents of a
text file and returns it:

    class FileReader(object):

        __metaclass__ = fakeable.Fakeable

        def read_file(self, path):
            with io.open(path, "rt", encoding="utf8"):
                contents = f.read()
            return contents

Then consider this class from production code that makes use of it:

    def file_contains(path, s):
        reader = FileReader()
        contents = reader.read_file("config.ini")
        found = (s in contents)
        return found

When the file_contains() method is invoked outside of unit tests everything
will work as expected: the real FileReader.read_file() method will be invoked.
However, during unit tests, a fake version of the FileReader class can be used
instead:

    class FakeFileReader(object):
        def read_file(self, path):
            raise IOError("file not found")

    class Test_FileReader(unittest.TestCase):
        def test_file_contains(self):
            fakeable.set_class("FileReader", FakeFileReader)
            with self.assertRaises(IOError):
                file_contains("blah_blah", "hey ho")

When file_contains() is invoked after invoking fakeable.set_class() the call to
"reader = FileReader()" will actually return an instance of FakeFileReader
instead of an instance of the *real* FileReader class.

This is achieved through the magic of metaclasses.

See the documentation in the "doc" folder for more details.
