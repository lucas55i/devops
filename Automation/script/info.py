import argparse
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from os import makedirs, path
from urllib import parse
from urllib.parse import ParseResult, urlencode

import pytz
import requests


class HostInventory:
    def __init__(self, url: str, inventory_id: str, host_ip: str, host_os: str,  username, password):
        if not (url and isinstance(url, str)):
            raise ValueError("Does not exist AWX URL")

        result: ParseResult = parse.urlparse(url, scheme='https')
        if not result.netloc:
            raise ValueError(f'Invalid URL ("{url}")')

        if not (inventory_id and isinstance(inventory_id, str)):
            raise ValueError("Does not exist inventory_id")

        if not (host_ip and isinstance(host_ip, str)):
            raise ValueError("Does not exist host_ip")

        if not (host_os and isinstance(host_os, str)):
            raise ValueError("Does not exist host_os")

        if not (username and isinstance(username, str)):
            raise ValueError("Does not exist username")

        if not (password and isinstance(password, str)):
            raise ValueError("Does not exist password")

        self.api_url = url
        self.api_token = None
        self.username = username
        self.password = password
        linux_inventory = inventory_id  # Verificar se esta certo.
        windows_inventory = inventory_id

        self.linux_inventory_id = int(linux_inventory)
        self.windows_inventory_id = int(windows_inventory)

        self.default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8'
        }
        self.default_request_timeout = 45

        try:
            response = requests.post(f"{self.api_url}/api/v2/ping",
                                     headers=self.default_headers,
                                     timeout=self.default_request_timeout)
            if response.status_code != 200:
                logging.error(f'The URL "{self.api_url}" could not be checked. '
                              f'Status code: {response.status_code}. '
                              f'Reason: {response.reason}: {response.text}. ')
                raise ConnectionError(f'{response.reason}')

            application = response.json().get('active_node', 'Null')
            version = response.json().get('version', 'Null')
            logging.info(
                f'URL "{self.api_url}" checked. Running "{application}" version "{version}"')

        except Exception as e:
            logging.error(str(e))
            raise ConnectionError(f'Error: "{str(e)}"')

        if not self.api_token:
            self.get_api_token()
            self.check_api_token()

    def get_api_token(self):
        logging.info(
            f'Trying to retrieve an API token for user "{self.username}"')

        try:
            response = requests.get(
                f'{self.api_url}/api/v2/me',
                headers=self.default_headers,
                auth=(self.username, self.password),
                timeout=self.default_request_timeout
            )

            if response.status_code != 200:
                logging.error(f'Could not login as "{self.username}". '
                              'Please check credentials. '
                              f'Status code: {response.status_code}'
                              f'Reason: {response.reason}: {response.text}')
                raise ConnectionError(response.reason)

            # get endpoints
            response_body = response.json() or {}
            results = response_body.get('results', [{}])
            username = results[0].get('username')
            user_id = results[0].get('id')
            personal_tokens_endpoint = results[0].get(
                'related', {}).get('personal_tokens')

            logging.info(
                f'Retrieving token for user "{username}" (id: "{user_id}")')

            # get token
            response = requests.post(
                f'{self.api_url}{personal_tokens_endpoint}',
                headers=self.default_headers,
                auth=(self.username, self.password),
                timeout=self.default_request_timeout
            )
            if response.status_code != 201:
                logging.error(f'Could not retrieve token for "{self.username}". '
                              'Please check credentials. '
                              f'Status code: {response.status_code} '
                              f'Reason: {response.reason}: {response.text}')
                raise ConnectionError(response.reason)

            response_body = response.json() or {}
            expires = response_body.get('expires')
            logging.info(f'Retrieved new token for user "{username}". '
                         f'Expires: "{expires}" ')
            self.api_token = response_body.get('token')
            self.default_headers.update({
                'Authorization': f'Bearer {self.api_token}'
            })

        except Exception as e:
            logging.error(f'Failed to retrieve a new token: {str(e)}')
            raise ConnectionError(str(e))

    def check_api_token(self) -> bool:
        logging.info(
            f'Checking authentication to AWX using API Token for user "{self.username}"')

        try:
            response = requests.get(
                f'{self.api_url}/api/v2/me',
                headers=self.default_headers,
                timeout=self.default_request_timeout
            )

            if response.status_code != 200:
                logging.error('Could not authenticate using API Token. '
                              f'Status code: {response.status_code}. '
                              f'Reason: {response.reason}: {response.text}. ')
                return False
            response_body = response.json() or {}
            results = response_body.get('results', [{}])
            username = results[0].get('username')
            last_login = results[0].get('last_login')
            user_id = results[0].get('id')
            logging.info(f'Valid Token for user "{username}" (id: "{user_id}"). '
                         f'Last login: "{last_login}"')
            return True
        except Exception as e:
            logging.error(f'Failed to check authentication to AWX: {str(e)}')
            raise ConnectionError(str(e))

    def searchHost(self, host_ip: str, host_os: str):
        """
        """
        if not isinstance(host_ip, str):
            logging.error(f'Host Ip: {host_ip} invalid. \
                        It must be string value.')
            raise ValueError

        if not isinstance(host_os, str):
            logging.error(f'Host OS: {host_os} invalid. \
                        It must be string value.')
            raise ValueError

        elif host_os.upper() == 'OS.LINUX':
            inventory_id = self.linux_inventory_id
        elif host_os.upper() == 'OS.WINDOWS':
            inventory_id = self.windows_inventory_id
        else:
            err_msg = f'Invalid OS "{host_os}". It must be either OS.LINUX or OS.WINDOWS'
            logging.error(err_msg)
            raise ValueError(err_msg)

        logging.info(f'Received Host IP: {host_ip} and Host OS: {host_os}')
        logging.info(
            f'Looking up to see if host "{host_ip}" is already on any AWX hosts...')

        try:
            response = requests.get(
                f'{self.api_url}/api/v2/hosts/?name={host_ip}',
                headers=self.default_headers,
                timeout=self.default_request_timeout
            )
            result = response.json()
            if response.status_code != 200:
                err_msg = f"Could not check if host is enabled. \
                                Status code: {response.status_code}, Reason: {response.reason}. \
                                Text: {response.text}'"
                logging.error(err_msg)
                return False

            if result['count'] != 0:
                nameInventory = result['results'][0]['summary_fields']['inventory']['name']
                logging.info(
                    f'Host "{host_ip}", already registered in the inventory "{nameInventory}"')
            else:
                self.includeHostInventory(host_ip, inventory_id)

        except Exception:
            logging.error('Error when trying to check/include host.')
            return False

    def includeHostInventory(self, host_ip: str, inventory_id: int):
        """
        """
        logging.info(
            f'Including host: "{host_ip}" in inventory: "{inventory_id}"')

        payload = {'name': host_ip, 'inventory': inventory_id}
        response = requests.post(
            f'{self.api_url}/api/v2/hosts/',
            headers=self.default_headers,
            json=payload,
            timeout=self.default_request_timeout
        )

        if response.status_code != 201:
            err_msg = f"Could not check if host is enabled and could include it \
                                into AWX hosts' list \
                                Status code: {response.status_code}, Reason: {response.reason}. \
                                Text: {response.text}"
            logging.error(err_msg)
            return False
        logging.info(f'Host "{host_ip}" successfully included on AWX '
                     f'at inventory "{inventory_id}"')
        return True


def logging_code(log_level=logging.INFO):
    logging.basicConfig(level=log_level)
    log = path.join('./log', 'main_logs')
    tmp = path.join('/tmp', 'main_logs')
    wrn_msg = None
    try:
        if path.isdir(tmp):
            log = tmp
        elif not path.isdir(log):
            makedirs(log)
    except PermissionError as err:
        wrn_msg = str(err)
        wrn_msg += '. Logs salvos em "%s".' % tmp
        if not path.isdir(tmp):
            makedirs(tmp)
            log = tmp

    logfile = path.join(log, path.basename(
        __file__).replace('.py', '.log'))
    logging.getLogger().addHandler(TimedRotatingFileHandler(logfile,
                                                            when='midnight',
                                                            backupCount=31,
                                                            encoding='utf-8'))
    log_formatter = logging.Formatter(
        "%(asctime)s\t[%(levelname)8s]\t%(message)s")
    log_formatter.formatTime = (lambda record, datefmt:
                                datetime.fromtimestamp(
                                    record.created, pytz.timezone('America/Sao_Paulo'))
                                .isoformat())

    for h in logging.getLogger().handlers:
        h.setFormatter(log_formatter)
        h.setLevel(log_level)

    if wrn_msg:
        logging.getLogger().warning(wrn_msg)


def main():
    logging_code()
    logging.info("=====START=====")
    parser = argparse.ArgumentParser(description='Scrhost_ipt Inventario AWX')
    parser.add_argument('--url', required=True, help="AWX API URL")
    parser.add_argument('--inventory_id', required=True,
                        help="inventory_id Host")
    parser.add_argument('--host_ip', required=True, help="host_ip Host")
    parser.add_argument('--host_os', required=True, help="host_os Host")
    parser.add_argument('--username', required=True, help="AWX username")
    parser.add_argument('--password', required=True, help="AWX password")
    args = parser.parse_args()

    try:
        data = {'url': args.url, 'inventory_id': args.inventory_id, 'host_ip': args.host_ip,
                'host_os': args.host_os, 'username': args.username, 'password': args.password}
        hostInventory = HostInventory(
            args.url, args.inventory_id, args.host_ip, args.host_os, args.username, args.password)
        success = hostInventory.searchHost(data["host_ip"], data["host_os"])
    except (AttributeError, RuntimeError) as err:
        logging.error(str(err))
        raise err
    except Exception as ex:
        logging.exception(str(ex), exc_info=ex)
        raise ex
    finally:
        logging.info('======END=======')


if __name__ == '__main__':
    main()
