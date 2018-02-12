import json
import logging
import os

try:
    from urllib.parse import urlparse
except ImportError:
    # Python < 3.0 compat
    from urlparse import urlparse

from docker import APIClient as DockerAPIClient
from docker import DockerClient, auth as docker_auth

from .requests_aws4auth import AWS4Auth

log = logging.getLogger(__name__)

# The docker library performs config file validation before we can get
# to it, so we need to override the config filename. The hyper config
# is still a valid Docker config file, it just has an additional key.
docker_auth.DOCKER_CONFIG_FILENAME = os.path.join('.hyper', 'config.json')


class APIClient(DockerAPIClient):
    # This is the Docker API version that Hyper currently
    # supports. The docker library uses a higher API version
    # by default so we need to set this explicity.
    API_VERSION = '1.23'
    DEFAULT_REGION = 'us-west-1'

    def __init__(self, config, **kwargs):
        self.config = config
        clouds = config.get('clouds')
        if not isinstance(clouds, dict):
            log.debug('Invalid config')
            raise RuntimeError('Invalid config')

        cloud_list = list(clouds.items())
        if len(cloud_list) != 1:
            log.debug('Invalid config')
            raise RuntimeError('Only one cloud is support in the config.')

        url, self.creds = cloud_list[0]
        url = urlparse(url)
        # The default endpoint URL can contain a wildcard for the region
        # subdomain so we need to make sure we replace that with a valid
        # region when building the base_url.
        base_url = 'https://{}'.format(url.netloc.replace('*', self.creds['region']))

        super(APIClient, self).__init__(
            base_url, version=APIClient.API_VERSION, tls=True, **kwargs)
        self.auth = AWS4Auth(self.creds['accesskey'], self.creds['secretkey'],
                             self.creds['region'], 'hyper')


class Client(DockerClient):
    DEFAULT_CONFIG_FILE = '~/.hyper/config.json'

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

    @classmethod
    def from_env(cls):
        log.debug('Looking for auth config')

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

        if endpoint and accesskey and secretkey:
            config = cls.config_object(endpoint, accesskey, secretkey, region)
            print('Found config in memory')
            return cls(config=config)

        log.debug('No auth config in memory - loading from filesystem')

        # Config not found in environment variables.
        default_config_file = os.path.expanduser(cls.DEFAULT_CONFIG_FILE)

        if os.path.isfile(default_config_file):
            # We don't read the file here as we allow the user to
            # pass the location to a config file, or a config object
            # during initialisation.
            config = json.load(open(default_config_file))
            print('Found config in default file.')
            return cls(config=config)

        if not (endpoint and accesskey and secretkey):
            log.debug('No auth config found')
            raise RuntimeError('Unable to guess config from default file or environment.')

    def __init__(self, config, **kwargs):
        # config = kwargs.get('config')
        if isinstance(config, str):
            # Assume config is a file path.
            config = json.load(open(os.path.expanduser(config)))
        if not isinstance(config, dict):
            raise TypeError('Invalid config object')
        self.api = APIClient(config, **kwargs)


from_env = Client.from_env
