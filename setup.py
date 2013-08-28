import io
import re
import distutils.core

# Read the long description from README.txt
with io.open("README.txt", "rt", encoding="utf8") as f:
    long_description = f.read()

# Read the version number from fakeable.py
version = None
with io.open("fakeable.py", "rt", encoding="utf8") as f:
    for line in f:
        match = re.match('^__version__ = "(?P<version>[^"]*)"$', line.strip())
        if match is not None:
            version = match.group("version")
            break
if version is None:
    raise Exception("unable to find version in fakeable.py")

distutils.core.setup(
    name="fakeable",
    version=version,
    description="enables seamless replacement of \"real\" objects "
        "with \"fake\" objects during unit testing",
    long_description=long_description,
    author="Denver Coneybeare",
    author_email="denver@sleepydragon.org",
    url="https://github.com/sleepydragonsw/fakeable",
    py_modules=["fakeable"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    license="Apache License version 2.0",
    keywords=["fake", "faking", "mock", "mocking"],
)
