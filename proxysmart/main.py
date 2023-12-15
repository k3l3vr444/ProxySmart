import logging
from datetime import datetime
import pprint
from urllib.parse import urlunparse, urlparse

import requests

from .exception import IncorrectResponseStatusCode
from .types.modem import Modem, ModemBandwidth
from .types.server import Server

logger = logging.getLogger(__name__)


class ProxySmart:
    def __init__(self, server: Server):
        self.server = server

    def create_url(self,
                   path: str | None = None,
                   query: dict | None = None):
        url = urlparse(str(self.server.url))
        if path:
            url = url._replace(path=path)
        if query:
            query_ = "?".join(f"{key}={value}" for key, value in query.items())
            url = url._replace(query=query_)
        return urlunparse(url)

    def _get(self,
             path: str | None = None,
             query: dict | None = None):
        return requests.get(self.create_url(path, query),
                            auth=(self.server.login, self.server.password))

    def _post(self,
              path: str | None = None,
              query: dict | None = None,
              data: dict | None = None):
        return requests.post(self.create_url(path, query),
                             auth=(self.server.login, self.server.password),
                             data=data)

    @staticmethod
    def _parse_modem(dct: dict) -> Modem:
        reset_secure_link = dct.get('RESET_SECURE_LINK')
        rotation_link = reset_secure_link.get('URL') if reset_secure_link else None
        if not reset_secure_link:
            logger.warning(f"Failed parsing modem rotation link: {pprint.pformat(dct)}")
        return Modem(imei=dct['modem_details']['IMEI'],
                     http=dct['proxy_creds']['HTTP_PORT'],
                     socks5=dct['proxy_creds']['SOCKS_PORT'],
                     nickname=dct['modem_details']['NICK'],
                     login=dct['proxy_creds']['LOGIN'],
                     password=dct['proxy_creds']['PASS'],
                     rotation_link=rotation_link
                     )

    @staticmethod
    def _parse_modem_bandwidth(dct: dict) -> ModemBandwidth:
        return ModemBandwidth(imei=dct['IMEI'],
                              in_=dct['bandwidth_bytes_lifetime_in'],
                              out=dct['bandwidth_bytes_lifetime_out'],
                              )

    def get_modems(self) -> list[Modem]:
        logger.debug(f"Requesting modems' statuses")
        response = self._get(path='apix/show_status_json')
        dct = response.json()
        logger.debug(f"Modems statuses: {pprint.pformat(dct)}")
        return [self._parse_modem(x) for x in response.json()]

    def get_modem(self, imei: str) -> Modem:
        logger.debug(f"Requesting modem's status")
        response = self._get(path=f'apix/show_single_status_json?arg={imei}')
        dct = response.json()
        logger.debug(f"Modem's status: {pprint.pformat(dct)}")
        return self._parse_modem(dct[0])

    def reboot_modem(self, imei: str):
        logger.debug(f"Rebooting modem")
        response = self._post(path=f'apix/reboot_modem_by_imei', data={"IMEI": imei})
        dct = response.json()
        logger.debug(f"Modem's status: {pprint.pformat(dct)}")

    def set_modem_data(self,
                       imei: str,
                       name: str,
                       http: int,
                       socks: int,
                       login: str,
                       password: str,
                       auto_ip_rotation: int,
                       valid_before: datetime):
        form_data = {'IMEI': imei,
                     'name': name + '1',
                     'http_port': http,
                     'socks_port': socks,
                     'proxy_login': login,
                     'proxy_password': password,
                     'AUTO_IP_ROTATION': auto_ip_rotation,
                     'PROXY_VALID_BEFORE': valid_before.strftime("%Y-%m-%dT%H:%M"),
                     'PHONE_NUMBER': '',
                     'mtu': '',
                     'bandlimin': '',
                     'bandlimout': '',
                     'bw_quota': '',
                     'connlim': '',
                     'TARGET_MODE': ''
                     }

        logger.debug(f'Requesting setting new modem\'s data: {form_data}')
        response = self._post(path=f'conf/edit/{imei}',
                              data=form_data)
        if response.status_code != 200:
            raise IncorrectResponseStatusCode(message=f"Failed setting modem: {imei} data",
                                              response=response)
        logger.info(f'New data has been set for modem: {imei}')

    def apply_settings(self, imei: str):
        logger.debug(f'Requesting modem\'s settings apply')
        response = self._post(path=f'modem/settings',
                              data={'imei': imei})
        if response.status_code != 200:
            raise IncorrectResponseStatusCode(message=f"Failed apply settings for modem: {imei}",
                                              response=response)
        logger.info(f'Applied settings for modem: {imei}')

    def bandwidth_report(self) -> list[ModemBandwidth]:
        logger.debug(f"Requesting modems' statuses")
        response = self._get(path='apix/bandwidth_report_json_all')
        return [self._parse_modem_bandwidth(x) for x in response.json()]

    def reset_bandwidth(self, imei: str):
        logger.debug(f'Requesting modem\'s bandwidth reset')
        response = self._post(path=f'apix/bandwidth_reset_counter',
                              query={'arg': imei},
                              data={'imei': imei})
        if response.status_code != 200:
            raise IncorrectResponseStatusCode(message=f"Failed modem\'s : {imei} bandwidth reset.",
                                              response=response)
        logger.info(f'The modem\'s : {imei} bandwidth has been reset.')

    def server_stats(self):
        logger.debug(f'Requesting modem\'s server stats')
        response = self._get(path='conf/server_stats')
        if response.status_code != 200:
            raise IncorrectResponseStatusCode(message=f"Failed servers\'s : {self.server.url} stats request.",
                                              response=response)
        return response
