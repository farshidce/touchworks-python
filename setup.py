#
# Please see the License.txt file for more information.
# All other rights reserved.
#
"""
Allscripts Touchworks API Client for Python
-------------------------------------------
The Allscripts Touchworks API Client makes it wasy to
interact with the Touchworks Platform APIs when writing client
applications in Python.

The Allscripts Touchworks API Client for Python is distributed under
the MIT License.
"""
from setuptools import setup

setup(
    name="touchworks",
    version="0.2",
    license="MIT",
    author="Farshid Ghods",
    author_email="farshid.ghods@gmail.com",
    url="https://github.com/farshidce/touchworks-python",
    download_url="https://github.com/farshidce/touchworks-python/tarball/0.2",
    description="Allscripts Touchworks API Client for Python",
    packages=["touchworks"],
    platforms="any",
    zip_safe=False,
    install_requires=[
        "requests>=2.3.0"
    ],
    tests_require=[
        "nose>=1.3.7"
    ],
    test_suite="nose.collector",
    keywords=["health", "api", "touchworks", "ehr"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
