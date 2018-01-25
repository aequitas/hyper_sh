from unittest.case import SkipTest

from hyper_sh import APIClient


def assertSetup():
    try:
        APIClient.guess_config()
    except Exception:
        raise SkipTest("no default config is detected")


def test_list_images():
    assertSetup()
    c = APIClient()  # guess config
    assert len(c.images()) != 0


def test_create_container():
    assertSetup()
    c = APIClient()  # guess config
    cid = c.create_container("busybox")
    c.remove_container(cid, force=True)
