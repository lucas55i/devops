#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#################################################
# Author: Lucas Silva <lucas_55i@outlook.com>
# Date: 2023-09-23
# Version: 1.0
# Runtime: Python 3.10
#################################################

# python3 move_files.py --source_folder './abc'  --destination_folder './wyz' --file_format 'app.[a-z][a-z]?'

import re
import os
import shutil
import logging
import argparse
import pytz
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class MoveFiles:
    def __init__(self, source_folder: str, destination_folder: str, file_format: str):
        if not os.path.isdir(source_folder):
            raise ValueError(f"{source_folder} Is Not Directory.")

        if not os.path.isdir(destination_folder):
            raise ValueError(f"{destination_folder} Is Not Directory.")

        if not (file_format and isinstance(file_format, str)):
            raise ValueError("Does not exixst file_format")

        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.file_format = file_format
        self.moveFiles()

    def moveFiles(self) -> list:
        logging.info(f"Buscando os arquivos no formato: '{self.file_format}'")
        files_to_move = []
        pattern = re.compile(self.file_format)
        try:
            for file in os.scandir(self.source_folder):
                if pattern.fullmatch(file.name):
                    if os.path.ismount(file.path):
                        logging.info(
                            "ponto de montagem corresponde ao padrão do nome de arquivo, mas será ignorado.")
                    elif os.path.islink(file.path):
                        logging.warning(
                            f'Link "{file.path}" corresponde totalmente ao padrão de nome de arquivo, mas será ignorado.')
                    elif os.path.isdir(file.path):
                        logging.warning(
                            f'Directory "{file.path}" corresponde totalmente ao padrão de nome de arquivo, mas será ignorado.')
                    elif os.path.isfile(file.path):
                        files_to_move.append(file.name)
                        shutil.move(file.path, self.destination_folder)
        except PermissionError:
            logging.error("No permission to run the script")
        else:
            logging.info(
                f"Movendo os arquivos {files_to_move}, para '{self.destination_folder}'")


def logging_code(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level)
    log = os.path.join("./log", "move_files_logs")
    tmp = os.path.join("/tmp", "move_files_logs")
    wrn_msg = None
    try:
        if os.path.isdir(tmp):
            log = tmp
        elif not os.path.isdir(log):
            os.makedirs(log)
    except PermissionError as err:
        wrn_msg = str(err)
        wrn_msg += '. Logs salvos em "%s".' % tmp
        if not os.path.isdir(tmp):
            os.makedirs(tmp)
            log = tmp

    logfile = os.path.join(log, os.path.basename(
        __file__).replace(".py", ".log"))
    logging.getLogger().addHandler(
        TimedRotatingFileHandler(
            logfile, when="midnight", backupCount=31, encoding="utf-8"
        )
    )
    log_formatter = logging.Formatter(
        "%(asctime)s\t[%(levelname)8s]\t%(message)s")
    log_formatter.formatTime = lambda record, datefmt: datetime.fromtimestamp(
        record.created, pytz.timezone("America/Sao_Paulo")
    ).isoformat()

    for h in logging.getLogger().handlers:
        h.setFormatter(log_formatter)
        h.setLevel(log_level)

    if wrn_msg:
        logging.getLogger().warning(wrn_msg)


def main():
    logging_code()
    logging.info("=====START=====")
    parser = argparse.ArgumentParser(description="Move Files")
    parser.add_argument("--source_folder", required=True,
                        help="Origin of files")
    parser.add_argument(
        "--destination_folder", required=True, help="Destination folder"
    )
    parser.add_argument(
        "--file_format",
        required=True,
        help="File format to move to the destination folder",
    )

    args = parser.parse_args()

    try:
        data = {
            "source_folder": args.source_folder,
            "destination_folder": args.destination_folder,
            "file_format": args.file_format,
        }
        moveFiles = MoveFiles(
            args.source_folder, args.destination_folder, args.file_format
        )
        success = moveFiles
    except (AttributeError, RuntimeError) as err:
        logging.error(str(err))
        raise err
    except Exception as ex:
        logging.exception(str(ex), exc_info=ex)
        raise ex
    finally:
        logging.info("======END======")


if __name__ == "__main__":
    main()
