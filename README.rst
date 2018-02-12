Python client for Hyper.sh
==========================

.. image:: https://api.travis-ci.org/tardyp/hyper_sh.svg?branch=master
   :alt: Build Status

A wrapper around docker-py_ to support Hyper's authentication system.

Hyper uses Amazon's
`Signature Version 4 <https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html>`_
(dubbed AWS4) to authenticate against it's service. This library replaces's docker-py's auth
module with a patched version of requests-aws4auth_ AWS4.

Installation
============

::

    pip install hyper_sh

Usage
=====

As hyper_sh is a wrapper around docker-py, the API is the same.
See the `docker-py documentaiton <https://docker-py.readthedocs.io>`_.

The default usage, via the hyper_sh.from_env helper function, will
automatically discover your Hyper configuration from environment
variables and the default config file location:

.. code-block:: python

    import docker
    client = docker.from_env()
    print(client.images.list())

One area the Hyper client differs from the Docker client is in the loading
of config. The initializers of hyper_sh.Client and hyper_sh.APIClient
require a positional argument for the config.

This can be either the location of a Hyper config file:

.. code-block:: python

    from hyper_sh import Client
    client = Client('path/to/config.json')
    print(client.images.list())

or a valid Hyper config object:

.. code-block:: python

    from hyper_sh import Client
    client = Client({'clouds': {
        os.environ['HYPER_ENDPOINT']: {
            'accesskey': os.environ['HYPER_ACCESSKEY'],
            'secretkey': os.environ['HYPER_SECRETKEY']
        }
    }})
    print(client.images.list())

API support
===========

Hyper doesn't support the full Docker API so some features of docker-py will not work. See the
`Hyper_ API documentaiton <https://docs.hyper.sh/Reference/API/2016-04-04%20[Ver.%201.23]/>`_
for details of their Docker API support (features not supported will be marked as IGNORED).
Conversely, Hyper has features that do not exist in the Docker API, and these are not currently
supported by hyper_sh.

.. _docker-py: https://github.com/docker/docker-py
.. _requests-aws4auth: https://github.com/sam-washington/requests-aws4auth