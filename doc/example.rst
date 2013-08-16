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
