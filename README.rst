|version| |wheel| |python3|

Allscripts Touchworks Platform API Client for Python
=====================================================

Installation
------------

Install from PyPI_ using pip_

.. code-block:: bash

    $ pip install touchworks


Resources
---------

Report issues_ on GitHub


Quick start
-----------

.. code-block:: python

    import touchworks

    tw = TouchWorks('<url'>, '<your svc_username>' , '<your svc_password',
                    '<your app_name>')
    #optional parameter : cache_token=True
    #optional parameter: username : ehr_username

    # search for patients whose name matches F*
    patients = tw.search_patients(search_criteria='F*')



Authentication and Authorization
--------------------------------
Please see http://developer.allscripts.com/ for more information

.. code-block:: python

    import touchworks

    tw = TouchWorks('<url'>, '<your svc_username>' , '<your svc_password',
                    '<your app_name>', '<ehr username>)

Error Handlng
---------------------------------

All supported APIs right now raise an exception of type TouchWorksException where the string
will contain the error received from the TouchWorks WebService APIs.

## example 1:
service username or password is invalid:
.. code-block:: python

	touchworks.api.http.TouchWorksException: unable to acquire the token from web service

## example 2:
SaveNot action failed
.. code-block:: python

	touchworks.api.http.TouchWorksException: magic json api failed : Error converting data type varchar to numeric.

## logging
in order to enable debugging user can set the logging level to DEBUG.when DEBUG is enabled
the library will print out each request and response in the logs.


## Developers

### build

.. code-block:: bash

	make

### test

.. code-block:: bash
	make tests

### add supprt for new APIs

TBD 

Supported Python Versions
-------------------------

This library aims to support and is tested against these Python versions:

* 2.7.6
* 3.4.0
* PyPy

License
-------

See LICENSE_ for details.

.. _documentation: http://developer.allscripts.com/
.. _issues: https://github.com/farshidce/touchworkds/issues
.. _PyPI: https://pypi.python.org/pypi
.. _pip: https://pypi.python.org/pypi/pip
.. _LICENSE: LICENSE.txt
.. _IPython: http://ipython.org/

.. |version| image:: https://badge.fury.io/py/pokitdok.svg
    :target: https://pypi.python.org/pypi/touchworks/

.. |wheel| image:: https://pypip.in/wheel/touchworks/badge.png
    :target: https://pypi.python.org/pypi/touchworks/

.. |python3| image:: https://caniusepython3.com/project/touchworks.svg
    :target: https://caniusepython3.com/project/touchworks