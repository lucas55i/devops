from os import listdir, remove
from platform import system
from pathlib import Path
import argparse
import logging


def death_row(files_in_path: list = [], seats=2) -> list:
    """This function is a method to select files to be purged.
        Its logic has been implemented to tickets 477187 and 477180.
        Parameters:
            files_in_path: list
                    A list containing files at the directory
            seats: int
                    The quantity of files that should be kept.
        Returns list cointaining files that should be purged.

        """
    from datetime import datetime
    logger = logging.getLogger(purge_files.__qualname__)

    death_row: list = []  # Files that should be purged
    list_of_files: list = []  # Aux list containing sorted tuples (filename, date)
    splited_filename: str = ''  # aux string

    # For this logic, files' names are in PT-BR.
    # Dict cointaining translations to EN-US to be used with datetime
    translated_months_name = {'Jan': 'Jan', 'Fev': 'Feb', 'Mar': 'Mar',
                              'Abr': 'Apr', 'Mai': 'May', 'Jun': 'Jun',
                              'Jul': 'Jul', 'Ago': 'Aug', 'Set': 'Sep',
                              'Out': 'Oct', 'Nov': 'Nov', 'Dez': 'Dec'}
    # If the quantity of files at the directory is less than the seats avaiable,
    # returns [], all files should be kept
    if len(files_in_path) <= seats:
        return []
    else:
        for file in files_in_path:
            try:
                try:
                    # For files matching ticket 477180
                    splited_filename = file.split('.')[1].replace('log', '')
                except:
                    # Filters files that are not related to ticket 477180
                    pass
                # Filters files that must be kept and doesn't match the logic
                if len(splited_filename) >= 8:
                    # Converts to datetime
                    date_from_file = datetime.strptime(splited_filename, '%Y%m%d')
                    list_of_files.append([file, date_from_file])
                else:
                    # For files matching ticket 477187, filters files that
                    # are not related to ticket 477187
                    splited_filename = file.split('-')
                    # Filters files that must be kept and doesn't match the logic
                    if len(splited_filename) > 3:
                        # Converts to datetime
                        time = splited_filename[4].split('.')[0]
                        date_from_file = datetime.strptime(
                            splited_filename[0] + '-' + translated_months_name[splited_filename[1]] + \
                            '-' + splited_filename[2] + ' ' + time, '%Y-%b-%d %H%M')
                        list_of_files.append([file, date_from_file])
            except Exception as e:
                logger.error(f'Failed to apply method\'s logic to file "{file}". '
                             'Probably runing the wrong method for this directory')
    # Sorts the tuples due to date
    list_of_files = sorted(list_of_files, key=lambda tuple: tuple[1])
    death_row = [item[0] for item in list_of_files[:len(list_of_files) - seats]]
    return death_row


def purge_files(directory: str = '', method=death_row, seats=2) -> int:
    '''This function is responsible for purging files.
        Parameters:
            directory: str
                    The directory where files will be purged
            method: function
                    This is a function responsible for returning
                    a list cointaining which files should be deleted.
                    It must receives a list of files and the number
                    of seats (quantity of files that shouldn't be purged).
                    It will be called by this current function.
            seats: int
                    The quantity of files that shouldn't be purged.
        Returns int as success or error code:
            0: success
            1: Missing parameter method
            2: Parameter method is not a function
            3: Directory not found
            4: Failed to remove file
            5: Some files couldn't be purged

            '''
    logger = logging.getLogger(purge_files.__qualname__)
    # A method to apply a logic of purging files. Receives the list of files
    # at the directory and seats (number o files that should be kept) as required parameters.
    # This method should return the list with files' names to be purged. 
    if not method:
        logger.critical('Error 1: No method included to perform action')
        return 1
    elif not hasattr(method, '__call__'):
        logger.critical('Error 2: Parameter method is not a function.')
        return 2
    # In case of windows, it uses double backslash.
    # For linux, single slash
    if system().lower() == 'windows':
        slash: str = '\\'
    else:
        slash: str = '/'

    path = Path(directory)
    logger.info(f'Directory: {path} ')
    # print(f'Directory: {path} ')

    # List all files at the directory, sends to the method parameter
    # receives the death row list with files that should be purged
    # Successfully purged files will be appended to dead_row list
    try:
        files_in_path: list = listdir(path)
    except:
        logger.critical('Error 3: Directory not found')
        return 3  # All files at the directory
    death_row: list = method(files_in_path=files_in_path, seats=seats)  # Files that should be purged
    dead_row: list = []  # Purged files

    for file in death_row:
        path_to_file = Path(directory + slash + file)
        # Removes file and check if still exists at the directory
        # Print errors and keep purging the others
        try:
            remove(path_to_file)
            if path_to_file.is_file():
                logger.error(f'Couldnt purge file "{file}".It still exists')
            else:
                logger.info(f'File "{file}" purged')
                dead_row.append(file)
        except Exception as e:
            logger.critical(f'Error 4: Could not remove file "{file}"', exc_info=True)

    files_after_purge: list = listdir(path)  # Files remaining at the directory
    logger.info('\n\nResult: '
                f'\n{len(files_in_path) - len(files_after_purge)} files purged'
                f'\n{len(files_after_purge)} files remaining in path.')
    logger.debug(f'Files expected to purged: "{death_row}"')
    logger.debug(f'Files purged: "{dead_row}" ')
    logger.debug(f'Files Remainig in path: "{files_after_purge}".')

    if len(death_row) + len(files_after_purge) == len(files_in_path) or len(death_row) == 0 \
            and list(set(death_row) - set(dead_row)) == []:
        # Every file to be purged were successfully or nothing to be deleted
        return 0
    else:
        if len(death_row) + len(files_after_purge) > len(files_in_path):
            # Not all files to be purged were purged
            logger.error(f'Error 5: Some files could not be purged\n'
                         f'Files that failed to be purged:\n {list(set(death_row) & set(files_after_purge))}')
            return 5
        elif False:
            # Another kind of error
            return 9999


if __name__ == '__main__':
    __author__ = 'Pedro H. Bittencourt F. - 03312324'

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s  [ %(name)s ]  [ %(levelname)s ]  %(message)s', datefmt="%m/%d/%Y %H:%M:%S  %Z",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("logs.log"),
            logging.StreamHandler()]
    )
    logger.info(f'====START====')
    logger.info('Initializing...')

    parser = argparse.ArgumentParser(description='Purge files at a given directory '
                                                 'for tickets 477180 and 477187')
    parser.add_argument('-d', '--directory', help='Directory where files should be purged', required=True)
    parser.add_argument('-s', '--seats', help='Quantity of files the should be kept', required=True)
    parser.add_argument('-m', '--method', help='Funcion method to implement logic', required=False)
    args = parser.parse_args()

    if not args.method:
        method = death_row
    else:
        method = args.method
    logger.debug(f'Method set to {method}')

    # directory = 'C:\\Users\\pedrohbf\\Desktop\\test_dir'
    returned = purge_files(directory=str(args.directory), method=method, seats=int(args.seats))
    logger.info(f'returned code {returned}')
    logger.info(f'====END====')

# TODO
# STDOU E STDERR, LOGS ETC

# Horario log com timezone
# Nao apagar diretorios
# Citar arquivos ignorados
