# python3 main.py -path "./files" -regex "20[0-9][0-9]-[A-z][A-z][a-z]-[0-9][0-9]--[0-2][1|9]00.zip" # YYYY-mmm-dd--0900 | YYYY-mmm-dd--2100
# python3 main.py -path "./files" -regex "OrdersApi.log\d{8}" # OrdersApi.log20221001

import os
import pytz
import logging
import argparse
from datetime import datetime
from re import compile, findall
from os import path, stat, listdir, remove, makedirs
from logging.handlers import TimedRotatingFileHandler


class WITRemoveFiles:
    def __init__(self, data: dict):
        expected_keys = ('path', 'regex')
        if all([True if k in data.keys() else False for k in expected_keys]):
            self.path = data.get('path')
            self.regex = data.get(r'regex')
        else:
            expected_keys = tuple([f'"{k}"' for k in expected_keys])
            expected_keys = ', '.join(expected_keys)
            raise AttributeError(
                f'Input data is missing key(s): {expected_keys}')

        self.arquivos_apagados = []
        self.kept_files = []
        self.directory_search()

    def delete_files(self, file):
        fullpath = path.join(self.path, file)
        timestamp = stat(fullpath).st_ctime
        created = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        delta = now - created

        try:
            if delta.days < 0.2:
                logging.info(f'"{file}" file deleted from directory {self.path}')
                remove(fullpath)
                self.arquivos_apagados.append(file)
            else:
                logging.info('No deleted files')
        except PermissionError:
            logging.error('No permission to delete files')

    def directory_search(self):
        files = []
        try:
            if os.path.isdir(self.path):
                logging.info('Checking Files for Deletion!')
                for file in listdir(self.path):
                    file_format = findall(r'{}'.format(self.regex),
                                          file)
                    if file_format:
                        files.extend(file_format)
                        # self.delete_files(file)
                    else:
                        self.kept_files.append(file)
                print(sorted(files))
                logging.info(f'{len(self.arquivos_apagados)} deleted files')
                logging.info(f'{len(self.kept_files)} kept files ')
            else:
                logging.error(f'{self.path} Not an existing directory')
        except PermissionError:
            logging.error('There is no permission to run the script')


def logging_code(log_level=logging.DEBUG):
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
    log_formatter = logging.Formatter("%(asctime)s\t[%(levelname)8s]\t%(message)s")
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
    logging.info('=====START======')
    parser = argparse.ArgumentParser(  # Seperar em função, padrão solid
        description='Path to delete files.')
    parser.add_argument('-path', required=True,
                        help='Path to execute script')
    parser.add_argument('-regex', required=True,
                        help='Format to delete files')
    args = parser.parse_args()

    data = {'path': args.path, 'regex': args.regex}
    WITRemoveFiles(data)
    logging.info('======END=======')


if __name__ == '__main__':
    main()
