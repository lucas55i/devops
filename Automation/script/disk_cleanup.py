import argparse
import json
import logging
import os
import random
import re
import shutil
import sys
from datetime import datetime
from distutils.util import strtobool
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler


def setup_logging():
    class WarningFilter(logging.Filter):
        """
        Filter log records, accepting items with level equal to INFO or WARNING.
        If the environment variable 'DEBUG' is 'true', this class will also accept
        records with level equal to DEBUG.
        """
        enable_debug = os.getenv('DEBUG', 'False')
        enable_debug = bool(strtobool(enable_debug.lower()))

        def filter(self, record: logging.LogRecord) -> bool:
            if WarningFilter.enable_debug is True:
                return record.levelno in (logging.DEBUG, logging.INFO, logging.WARNING)
            else:
                return record.levelno in (logging.INFO, logging.WARNING)

    class ErrorFilter(logging.Filter):
        """Filter log records, accepting items with level equal to ERROR, CRITICAL, or FATAL."""

        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno >= logging.ERROR

    stdout = StreamHandler(sys.stdout)
    stdout.addFilter(WarningFilter('stdout_filter'))

    stderr = StreamHandler(sys.stderr)
    stderr.addFilter(ErrorFilter('stderr_filter'))

    logging.basicConfig(format='%(message)s', level=logging.NOTSET, handlers=(stdout, stderr))

    logdir = None
    logdirs = ('/opt/wem/log/', '/var/log/wit-execution-manager/', './', '~/wem/log/')
    for directory in logdirs:
        directory = os.path.abspath(os.path.expanduser(os.path.expandvars(directory)))
        if os.path.isdir(directory):
            logdir = directory
            break
        else:
            try:
                os.makedirs(directory)
            except PermissionError as err:
                logging.debug(str(err))
            else:
                logdir = directory
                break

    if logdir:
        filename = os.path.basename(__file__).replace('.py', '.log')
        filename = os.path.join(logdir, filename)
        logfile = TimedRotatingFileHandler(filename, when='midnight', backupCount=31,
                                           encoding='utf-8')  # append mode by default
        logfile.setFormatter(logging.Formatter('%(asctime)s\t[%(levelname)8s]\t%(message)s'))
        logging.getLogger().addHandler(logfile)


def __parse_arguments__():
    """Parse arguments from command line."""
    __descricao = 'Script que remove arquivos de um diretório, seguindo um padrão de nomes.'
    __nota = '*** Esse script foi desenvolvido para ser invocado por linha de comando, sem interatividade. ***'
    parser = argparse.ArgumentParser(description=__descricao, epilog=__nota)
    parser.add_argument('-d', '--directory', dest='directory', required=True,
                        help='Define o diretório de onde os arquivos devem ser excluídos.')
    parser.add_argument('-p', '--file-pattern', dest='pattern', required=True,
                        help='Expressão regular que estabelece o padrão dos nomes dos arquivos a serem excluídos.')
    parser.add_argument('-k', '--keep', type=int, dest='keep', required=True,
                        help='Quantidade de arquivos que correspondem ao padrão de nomes mas que devem ser mantidos.')

    return parser.parse_args()


def delete_files_by_name(directory: str, filename_pattern: str, keep: int, revert_sort=True) -> dict:
    """
    Delete files from a directory, based on their name pattern.

    :param directory: the absolute path of the directory where the files reside.
    :param filename_pattern: the name pattern that fully matches all the target files to be deleted.
    :param keep: the number of files that must be kept (instead of deleted), from the head of the list of
        matched files.
    :param revert_sort: whether the list of matched files should be sorted in reverse order.
    :return: a dictionary with a list of files removed, a list of files kept (not removed), and the total bytes deleted.
    """
    if not (directory and isinstance(directory, str)):
        raise ValueError('Argument "directory" must be a non-empty string.')
    if not (filename_pattern and isinstance(filename_pattern, str)):
        raise ValueError('Argument "filename_pattern" must be a non-empty string.')
    if not (isinstance(keep, int) and keep > 0):
        raise ValueError('Argument "keep" must be a non-negative integer.')
    if not (isinstance(revert_sort, bool)):
        raise ValueError('Argument "revert_sort" must be a boolean.')
    if not os.path.isdir(directory):
        raise ValueError(f'Directory {directory} does not exist.')

    logger = logging.getLogger(delete_files_by_name.__qualname__)

    file_list = []
    files_to_keep = []
    files_deleted = {}
    bytes_removed = 0

    pattern = re.compile(filename_pattern)
    try:
        for entry in os.scandir(directory):
            if pattern.fullmatch(entry.name):
                # links must be checked before files and directories
                if os.path.ismount(entry.path):
                    logger.warning(f'Mount point "{entry.path}" fully matches the filename pattern but will be '
                                   'ignored.')
                elif os.path.islink(entry.path):
                    logger.warning(f'Link "{entry.path}" fully matches the filename pattern but will be ignored.')
                elif os.path.isdir(entry.path):
                    logger.warning(f'Directory "{entry.path}" fully matches the filename pattern but will be ignored.')
                elif os.path.isfile(entry.path):
                    file_list.append(entry.path)
    except PermissionError:
        logger.error(f'Could not scan directory "{directory}".')
    else:
        file_list = sorted(file_list, reverse=revert_sort)  # FIXME essa ordenação não atende o problema do ticket 477187
        files_to_delete = file_list[keep:]
        files_to_keep = sorted(list(set(file_list) - set(files_to_delete)), reverse=revert_sort)
        logger.info(f'The following files are going to be kept:    {files_to_keep}.')
        logger.info(f'The following files are going to be removed: {files_to_delete}.')

        for f in files_to_delete:
            try:
                file_stat = os.stat(f, follow_symlinks=False)
                file_size = file_stat.st_size
                if os.name != 'nt':
                    # On some Unix systems (such as Linux), the attribute 'st_blocks' may be available
                    # and will be used to detect sparse files
                    if hasattr(file_stat, 'st_blocks') and file_stat.st_blocks == 0:
                        logger.info(f'File "{f}" is a sparse file')
                        file_size = 0
                os.remove(f)
                logger.info(f'File removed: "{f}"')
                files_deleted.update({f: file_size})
            except PermissionError:
                logger.error(f'Could not remove file "{f}". Permission denied.')
                files_to_keep.append(f)

        for f, s in files_deleted.items():
            bytes_removed += s

        expected = len(files_to_delete)
        real = len(files_deleted)
        if real == 0:
            logger.error('No file has been removed.')
        elif real != expected:
            logger.error(f'Not all the expected {expected} files could be removed. '
                         f'Only {real} files have been removed.')
        else:
            logger.info(f'{bytes_removed} bytes have been removed from directory "{directory}".')

    return {
        'removed': list(files_deleted.keys()),
        'kept': files_to_keep,
        'saved_space': bytes_removed
    }


def main():
    setup_logging()
    logger = logging.getLogger(main.__qualname__)
    parsed_args: argparse.Namespace = __parse_arguments__()
    start = datetime.now()
    try:
        directory = parsed_args.directory
        filename_pattern = parsed_args.pattern
        keep = parsed_args.keep
        result = delete_files_by_name(directory, filename_pattern, keep, True)
        logger.info('Files kept:\n%s' % json.dumps(result.get('kept', []), indent=True))
        logger.info('Files removed:\n%s' % json.dumps(result.get('removed', []), indent=True))
        logger.info('Saved space: %d bytes' % result.get('saved_space', -1))
    except MemoryError:
        logger.error('System has run out of memory!')

    end = datetime.now()
    logger.info(f'Operation duration: {(end - start).total_seconds():.1f} seconds')


def restaura_arquivos(delete_old: bool):
    # FIXME: remover esse método antes de publicar. Serve para testes durante desenvolvimento.
    origin1 = 'C:/Orders/Api'
    subdirs1 = ('OrdersApi.log20221027',)
    files1 = (
        'OrdersApi.log',
        'OrdersApi.log20221001', 'OrdersApi.log20221002', 'OrdersApi.log20221003', 'OrdersApi.log20221004',
        'OrdersApi.log20221005', 'OrdersApi.log20221006', 'OrdersApi.log20221007', 'OrdersApi.log20221008',
        'OrdersApi.log20221009', 'OrdersApi.log20221010', 'OrdersApi.log20221011', 'OrdersApi.log20221012',
        'OrdersApi.log20221013', 'OrdersApi.log20221014', 'OrdersApi.log20221015', 'OrdersApi.log20221016',
        'OrdersApi.log20221017', 'OrdersApi.log20221018', 'OrdersApi.log20221019', 'OrdersApi.log20221020',
        'OrdersApi.log20221021', 'OrdersApi.log20221022', 'OrdersApi.log20221023', 'OrdersApi.log20221024',
        'OrdersApi.log20221025', 'OrdersApi.log20221026'
    )
    origin2 = 'var/atlassian/application-data/jira/export/'
    subdirs2 = ('workflowexports/',)
    files2 = (
        'Credential Oz Fire.zip',
        'export jira bacen 2022-02-09.zip',
        '2022-Ago-20--0900.zip', '2022-Ago-20--2100.zip', '2022-Ago-21--0900.zip', '2022-Ago-21--2100.zip',
        '2022-Ago-22--0900.zip', '2022-Ago-22--2100.zip', '2022-Ago-23--0900.zip', '2022-Ago-23--2100.zip',
        '2022-Ago-24--0900.zip', '2022-Ago-24--2100.zip', '2022-Ago-25--0900.zip', '2022-Ago-25--2100.zip',
        '2022-Ago-26--0900.zip', '2022-Ago-26--2100.zip', '2022-Ago-27--0900.zip', '2022-Ago-27--2100.zip',
        '2022-Ago-28--0900.zip', '2022-Ago-28--2100.zip', '2022-Ago-29--0900.zip', '2022-Ago-29--2100.zip',
        '2022-Ago-30--0900.zip', '2022-Ago-30--2100.zip', '2022-Ago-31--0900.zip', '2022-Ago-31--2100.zip',
        '2022-Set-01--0900.zip', '2022-Set-01--2100.zip', '2022-Set-02--0900.zip', '2022-Set-02--2100.zip',
        '2022-Set-03--0900.zip', '2022-Set-03--2100.zip', '2022-Set-04--0900.zip', '2022-Set-04--2100.zip',
        '2022-Set-05--0900.zip', '2022-Set-05--2100.zip', '2022-Set-06--0900.zip', '2022-Set-06--2100.zip',
        '2022-Set-07--0900.zip', '2022-Set-07--2100.zip', '2022-Set-08--0900.zip', '2022-Set-08--2100.zip',
        '2022-Set-09--0900.zip', '2022-Set-09--2100.zip', '2022-Set-10--0900.zip', '2022-Set-10--2100.zip',
        '2022-Set-11--0900.zip', '2022-Set-11--2100.zip', '2022-Set-12--0900.zip', '2022-Set-12--2100.zip',
        '2022-Set-13--0900.zip', '2022-Set-13--2100.zip', '2022-Set-14--0900.zip', '2022-Set-14--2100.zip',
        '2022-Set-15--0900.zip', '2022-Set-15--2100.zip', '2022-Set-16--0900.zip', '2022-Set-16--2100.zip',
        '2022-Set-17--0900.zip', '2022-Set-17--2100.zip', '2022-Set-18--0900.zip', '2022-Set-18--2100.zip',
        '2022-Set-19--0900.zip', '2022-Set-19--2100.zip', '2022-Set-20--0900.zip', '2022-Set-20--2100.zip',
        '2022-Set-21--0900.zip', '2022-Set-21--2100.zip', '2022-Set-22--0900.zip', '2022-Set-22--2100.zip',
        '2022-Set-23--0900.zip', '2022-Set-23--2100.zip', '2022-Set-24--0900.zip', '2022-Set-24--2100.zip',
        '2022-Set-25--0900.zip', '2022-Set-25--2100.zip', '2022-Set-26--0900.zip', '2022-Set-26--2100.zip',
        '2022-Set-27--0900.zip', '2022-Set-27--2100.zip', '2022-Set-28--0900.zip', '2022-Set-28--2100.zip',
        '2022-Set-29--0900.zip', '2022-Set-29--2100.zip', '2022-Set-30--0900.zip', '2022-Set-30--2100.zip',
        '2022-Out-01--0900.zip', '2022-Out-01--2100.zip', '2022-Out-02--0900.zip', '2022-Out-02--2100.zip',
        '2022-Out-03--0900.zip', '2022-Out-03--2100.zip', '2022-Out-04--0900.zip', '2022-Out-04--2100.zip',
        '2022-Out-05--0900.zip', '2022-Out-05--2100.zip', '2022-Out-06--0900.zip', '2022-Out-06--2100.zip',
        '2022-Out-07--0900.zip', '2022-Out-07--2100.zip', '2022-Out-08--0900.zip', '2022-Out-08--2100.zip',
        '2022-Out-09--0900.zip', '2022-Out-09--2100.zip', '2022-Out-10--0900.zip', '2022-Out-10--2100.zip',
        '2022-Out-11--0900.zip', '2022-Out-11--2100.zip', '2022-Out-12--0900.zip', '2022-Out-12--2100.zip',
        '2022-Out-13--0900.zip', '2022-Out-13--2100.zip', '2022-Out-14--0900.zip', '2022-Out-14--2100.zip',
        '2022-Out-15--0900.zip', '2022-Out-15--2100.zip', '2022-Out-16--0900.zip', '2022-Out-16--2100.zip',
        '2022-Out-17--0900.zip', '2022-Out-17--2100.zip', '2022-Out-18--0900.zip', '2022-Out-18--2100.zip',
        '2022-Out-19--0900.zip', '2022-Out-19--2100.zip', '2022-Out-20--0900.zip', '2022-Out-20--2100.zip',
        '2022-Out-21--0900.zip', '2022-Out-21--2100.zip', '2022-Out-22--0900.zip', '2022-Out-22--2100.zip',
        '2022-Out-23--0900.zip', '2022-Out-23--2100.zip', '2022-Out-24--0900.zip', '2022-Out-24--2100.zip',
        '2022-Out-25--0900.zip', '2022-Out-25--2100.zip', '2022-Out-26--0900.zip', '2022-Out-26--2100.zip'
    )

    if delete_old is True:
        if os.path.isdir(origin1):
            os.rmdir(origin1)

    data = {
        '477180': {
            'origin': origin1,
            'subdirs': subdirs1,
            'files': files1
        # },
        # '477187': {
            # 'origin': origin2,
            # 'subdirs': subdirs2,
            # 'files': files2
        }
    }

    for k, v in data.items():
        origin = os.path.join('/tmp', v.get('origin'))
        if os.path.isdir(origin):
            if delete_old is True:
                shutil.rmtree(origin)
                os.makedirs(origin)
        else:
            os.makedirs(origin)
        for subdir in v.get('subdirs'):
            subdir = os.path.join(origin, subdir)
            if not os.path.isdir(subdir):
                os.makedirs(subdir)
        for file in v.get('files'):
            file = os.path.join(origin, file)
            if not os.path.isfile(file):
                with open(file, 'wb') as f:
                    r = random.Random()
                    f.write(r.randbytes(r.randint(1, 10240)))


if __name__ == '__main__':
    # restaura_arquivos(True)
    main()
