import io
import distutils.core

with io.open("README.txt", "rt", encoding="utf8") as f:
    long_description = f.read()

with io.open("VERSION.txt", "rt", encoding="utf8") as f:
    version = f.read().strip()

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
