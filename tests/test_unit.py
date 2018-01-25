import json
import os

from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    # Python < 3.3 compat
    from mock import patch

from hyper_sh import APIClient

config_path = os.path.join(os.path.dirname(__file__), 'hyper_config.json')


class TestConfig(TestCase):
    @patch.object(os, 'environ', {})
    @patch.object(APIClient, 'DEFAULT_CONFIG_FILE', 'no_file.json')
    def test_invalid_path(self):
        # Test no default file and no env vars.
        with self.assertRaises(RuntimeError):
            APIClient()

        # Test file can't be found.
        with self.assertRaises(IOError):
            APIClient('no_file.json')

        # Test invalid config.
        with self.assertRaises(KeyError):
            assert (APIClient({}))

        # Test invalid clouds.
        with self.assertRaises(RuntimeError):
            assert (APIClient({'clouds': {'a': {}, 'b': {}}}))

    def test_valid_config(self):
        # Test with valid env vars.
        with patch.object(
                os, 'environ', {
                    'HYPER_ENDPOINT': 'tcp://us-west-1.hyper.sh:443',
                    'HYPER_ACCESSKEY': 'abc123',
                    'HYPER_SECRETKEY': '321cba'
                }):
            assert (APIClient())

        # Test with valid config file.
        assert (APIClient(config_path))

        # Test with valid config object.
        config = json.load(open(config_path))
        assert (APIClient(config))

    def test_valid_base_url(self):
        config = json.load(open(config_path))
        c = APIClient(config)

        # Test base_url correct.
        assert (c.base_url == 'https://us-west-1.hyper.sh:443')

        # Test base_url includes correct region.
        endpoint = list(config['clouds'].keys())[0]
        region_config = {
            'clouds': {
                'tcp://eu-west-1.hyper.sh:443': config['clouds'][endpoint]
            }
        }
        c = APIClient(region_config)
        assert (c.base_url == 'https://eu-west-1.hyper.sh:443')

    def test_auth_has_config(self):
        config = json.load(open(config_path))
        clouds = list(config['clouds'].items())
        endpoint, creds = clouds[0]

        auth = APIClient(config).auth

        # Test that all config values are present and correct.
        assert (auth.access_id == creds['accesskey'])
        assert (auth.signing_key.secret_key == creds['secretkey'])
        assert (auth.region == creds['region'])
