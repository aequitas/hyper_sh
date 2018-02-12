import json
import os

from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    # Python < 3.3 compat
    from mock import patch

from hyper_sh import Client, APIClient, from_env

config_path = os.path.join(os.path.dirname(__file__), 'hyper_config.json')


class TestConfig(TestCase):
    @patch.object(os, 'environ', {})
    @patch.object(Client, 'DEFAULT_CONFIG_FILE', 'no_file.json')
    def test_invalid_path(self):
        # Test no default file and no env vars.
        with self.assertRaises(TypeError):
            Client()

        # Test file can't be found.
        with self.assertRaises(IOError):
            Client('no_file.json')

        # Test invalid config.
        with self.assertRaises(RuntimeError):
            Client({})

        # Test invalid clouds.
        with self.assertRaises(RuntimeError):
            Client({'clouds': {'a': {}, 'b': {}}})

    def test_valid_config(self):
        # Test with valid env vars.
        with patch.object(
                os, 'environ', {
                    'HYPER_ENDPOINT': 'tcp://us-west-1.hyper.sh:443',
                    'HYPER_ACCESSKEY': 'abc123',
                    'HYPER_SECRETKEY': '321cba'
                }):
            assert (isinstance(from_env(), Client))

        # Test with valid config file.
        assert (Client(config_path))

        # Test with valid config object.
        config = json.load(open(config_path))
        assert (Client(config))

    def test_lowercase_envvars(self):
        # Test with valid env vars.
        with patch.object(
                os, 'environ', {
                    'hyper_endpoint': 'tcp://us-west-1.hyper.sh:443',
                    'hyper_accesskey': 'abc123',
                    'hyper_secretkey': '321cba'
                }):
            assert (isinstance(from_env(), Client))

    def test_valid_base_url(self):
        config = json.load(open(config_path))
        api_client = APIClient(config=config)

        # Test base_url correct.
        assert (api_client.base_url == 'https://us-west-1.hyper.sh:443')

        # Test base_url includes correct region.
        endpoint = list(config['clouds'].keys())[0]
        region_config = {
            'clouds': {
                'tcp://eu-central-1.hyper.sh:443': config['clouds'][endpoint]
            }
        }
        api_client = APIClient(config=region_config)
        assert (api_client.base_url == 'https://eu-central-1.hyper.sh:443')

    def test_auth_has_config(self):
        config = json.load(open(config_path))
        clouds = list(config['clouds'].items())
        endpoint, creds = clouds[0]

        auth = APIClient(config).auth

        # Test that all config values are present and correct.
        assert (auth.access_id == creds['accesskey'])
        assert (auth.signing_key.secret_key == creds['secretkey'])
        assert (auth.region == creds['region'])
