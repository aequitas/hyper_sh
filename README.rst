Hyper_sh
========

.. image:: https://api.travis-ci.org/tardyp/hyper_sh.svg?branch=master
   :alt: Build Status

docker-py adapted to Hyper

It uses underscore '_' instead of '-' in its name like the original `Hyper_` service, but you can actually install either spelling.

This is a thin adaptation layer of docker-py for it to work with Hyper's credential scheme

Install from pip
================

::

    pip install hyper_sh

How to use
==========

hyper_sh is used with the same API as docker-py

::

    from hyper_sh import Client
    c = APIClient()  # without argument, config is guessed by reading ~/.hyper/config.json
    print c.images.list()

::

    from hyper_sh import APIClient
    c = APIClient("path/to/config.json")  # you can pass a specific config.json
    print c.images.list()

::

    from hyper_sh import APIClient
    c = APIClient({'clouds': {
        os.environ['HYPER_ENDPOINT']: {
            "accesskey": os.environ['HYPER_ACCESSKEY'],
            "secretkey": os.environ['HYPER_SECRETKEY']
        }
    }})  # or you can give the content of a config.json directly
    print c.images.list()

API
===
At the moment, hyper_sh maps 1:1 to the api of docker-py, which means that some api will not work,
as they are not supported by `Hyper_` - these will be marked as `IGNORED` in the `Hyper_` API docs.

https://docker-py.readthedocs.io
https://docs.hyper.sh/Reference/API/2016-04-04%20[Ver.%201.23]/

There are some other API supported by `Hyper_` that are not yet supported by this module (i.e. fip managment).
Patches are welcome.
