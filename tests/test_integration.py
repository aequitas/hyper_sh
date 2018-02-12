import os
import unittest

import hyper_sh

SKIP_MESSAGE = 'Hyper integration tests are for local testing only.'


@unittest.skipIf(os.environ.get('TRAVIS') == 'true', SKIP_MESSAGE)
def test_list_images():
    client = hyper_sh.from_env()
    images = client.images.list()
    assert len(images) != 0


@unittest.skipIf(os.environ.get('TRAVIS') == 'true', SKIP_MESSAGE)
def test_create_container():
    client = hyper_sh.from_env()
    container = client.containers.create('busybox')
    container.remove(force=True)
