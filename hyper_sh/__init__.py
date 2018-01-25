import json
import os

try:
    from urllib.parse import urlparse
except ImportError:
    # Python < 3.0 compat
    from urlparse import urlparse

from docker import DockerClient
from docker import APIClient as DockerAPIClient

from .requests_aws4auth import AWS4Auth


class APIClient(DockerAPIClient):
    DEFAULT_CONFIG_FILE = '~/.hyper/config.json'
    # This is the Docker API version that Hyper currently
    # supports. The docker library uses a higher API version
    # by default so we need to set this explicity.
    API_VERSION = '1.23'
    DEFAULT_REGION = 'us-west-1'

    @staticmethod
    def config_object(endpoint, accesskey, secretkey, region):
        return {
            'clouds': {
                endpoint: {
                    'accesskey': accesskey,
                    'secretkey': secretkey,
                    'region': region
                }
            }
        }

    @staticmethod
    def guess_config():
        default_config_file = os.path.expanduser(APIClient.DEFAULT_CONFIG_FILE)

        if os.path.isfile(default_config_file):
            # We don't read the file here as we allow the user to
            # pass the location to a config file, or a config object
            # during initialisation.
            return default_config_file

        keys = ['HYPER_ENDPOINT', 'HYPER_ACCESSKEY', 'HYPER_SECRETKEY', 'HYPER_REGION']

        endpoint, accesskey, secretkey, region = [os.environ.get(k) for k in keys]

        # The common standard is for environment variables to be
        # uppercase, but for backwards compatibility we need to
        # check for lowercase variables as well.
        if not (endpoint and accesskey and secretkey):
            endpoint, accesskey, secretkey, region = [
                os.environ.get(k.lower()) for k in keys
            ]

        region = region if region else APIClient.DEFAULT_REGION

        if not (endpoint and accesskey and secretkey):
            raise RuntimeError('Unable to guess config from default file or environment.')

        return APIClient.config_object(endpoint, accesskey, secretkey, region)

    def __init__(self, config=None):
        if config is None:
            config = self.guess_config()

        self.config = config

        if isinstance(config, str):
            # Assume config is a file path.
            self.config = json.load(open(os.path.expanduser(config)))

        clouds = list(self.config['clouds'].items())
        if len(clouds) != 1:
            raise RuntimeError('Only one cloud is support in the config.')

        url, self.creds = clouds[0]
        url = urlparse(url)
        # The default endpoint URL can contain a wildcard for the region
        # subdomain so we need to make sure we replace that with a valid
        # region when building the base_url.
        base_url = 'https://{}'.format(url.netloc.replace('*', self.creds['region']))

        DockerAPIClient.__init__(self, base_url, version=APIClient.API_VERSION, tls=True)

        self.auth = AWS4Auth(self.creds['accesskey'], self.creds['secretkey'],
                             self.creds['region'], 'hyper')


class Client(DockerClient):
    def __init__(self, *args, **kwargs):
        self.api = APIClient(*args, **kwargs)
