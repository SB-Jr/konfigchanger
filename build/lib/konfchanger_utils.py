"""
konfchanger_utils - a util module to assist konfchanger
Copyright (C) 2020 shrijit basak

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import os
import click
import shutil
import json
from subprocess import call

BAK_FILE_EXTENSION = '.bak'


class Utils:

    def __init__(self):
        self.__info_map = my_dict()
        self.logger = my_dict()

        self.__set_info_logger()
        self.__set_home_dir()
        self.__set_current_directory()
        self.__set_konfigchanger_config()
        self.__set_verbose(False)
        if not self.is_konfigchanger_config_present():
            return None
        self.__load_konfigchanger_config()
        pass


    def __set_info_logger(self):
        self.logger.info = click.echo


    def __set_home_dir(self):
        self.__info_map.home_dir = os.getenv('HOME')


    def __set_current_directory(self):
        self.__info_map.current_dir = os.getcwd()


    def __set_konfigchanger_config(self):
        current_path = self.get_current_directory()
        self.__info_map.konfigchanger_config = os.path.join(current_path, '.konfchanger_default_config')


    def __load_konfigchanger_config(self):
        konfigchanger_config = self.get_value('konfigchanger_config')
        with open(konfigchanger_config, 'r') as cfg:
            json_data = json.load(cfg)
            self.__info_map['store_dir'] = json_data['store_dir']
            self.__info_map['config_list_path'] = json_data['config_list_path']


    def __set_stored_config_list(self, stored_configs):
        self.__info_map.store_config_list = stored_configs


    def __set_verbose(self, verbose):
        '''Set verbose function to print verbose statements if verbose flag is set'''
        def identity(*args, **args1):
            pass
        self.logger.log = click.echo if verbose else identity

    def enable_verbose(self, ctx, flag_name, enable_flag=False):
        self.__set_verbose(enable_flag)


    def get_home_path(self):
        return self.get_value('home_dir')


    def get_current_directory(self):
        return self.get_value('current_dir')


    def get_konfigchanger_config(self):
        return self.get_value('konfigchanger_config')

    def get_config_list_path(self):
        return self.get_value('config_list_path')

    def is_konfigchanger_config_present(self):
        path = self.get_value('konfigchanger_config')
        if not os.path.isfile(path):
            self.logger.info('.konfchanger_default_config file doesnt not exist at '+path)
            self.logger.info('please create a .konfchanger_default_config file in this directory:'+ self.get_current_directory())
            self.logger.info('It should contain the following \{\n'+
                                '"store_dir":"<full_path_to_a_location_to_store_backups>",'+
                                '"config_list_path":"<path_to_a_file_containing_list_of_config_files_to_backup>"'+
                                '\}')
            return False
        else:
            self.logger.log('Config file Found!!')
            return True


    def is_config_list_path_present(self):
        '''Check if the file containing list to other configuration file to be backed up is present or not'''

        path = self.get_value('config_list_path')
        if not os.path.isfile(path):
            self.logger.info('Configuration List providing file not present at '+path)
            self.logger.info('Create a file at the above location with following contents:')
            self.logger.info('<relative_to_home_path_to_config_file_1>\n<relative_to_home_path_to_config_file_2>\n:\n<relative_to_home_path_to_config_file_n>')
            self.logger.info('any location which starts with a "#" will be ignored')
            return False
        else:
            self.logger.log('Configuration list providing file found')
            return True

    def is_store_dir_present(self):
        '''Checks if store directory is present or not'''

        store_dir = self.get_value('store_dir')
        if not os.path.isdir(store_dir):
            self.logger.info('Backup directory is not pesent!!')
            return False
        else:
            self.logger.log('Found Backup directory')
            return True


    def is_duplicate_name_present(self, name):
        name_path =  os.path.join(self.get_store_dir(), name)
        if os.path.isdir(name_path):
            self.logger.info('configuration backup with this name already exists')
            return True
        else:
            return False


    def get_value(self, key):
        '''Get value from info_map in the object'''

        if key in self.__info_map.keys():
            return self.__info_map[key]
        return None


    def get_stored_configs(self):
        '''Gets the list of stored configurations from store folder'''

        store_dir = self.get_value('store_dir')
        stored_configs = [config for config in os.listdir(store_dir)]
        if len(stored_configs) == 0:
            self.logger.info('Store directory does not contain any previously backed up configurations')
            return None
        else:
            self.__set_stored_config_list(stored_configs)
            return stored_configs

    def get_config_backup_absolute_path_by_name(self, name):
        return os.path.join(self.get_store_dir(), name)

    def get_store_dir(self):
        return self.get_value('store_dir')

    def get_config_name(self):
        '''Gives user the list of stored configs prvided in parameter and lets them choose one from the list'''

        self.echo_configs()
        stored_configs = self.get_value('store_config_list')
        if stored_configs is None:
            self.logger.info('No backed up configuration packs present!!\nBackup folder is empty')
            return
        no_configs = len(stored_configs)
        value = click.prompt('Please enter the number associated with the configuration, you want to choose:', type=click.IntRange(1, no_configs))
        name = stored_configs[value - 1]
        return name


    def echo_configs(self):
        '''Prints the stored config list passed'''

        stored_configs = self.get_value('store_config_list')
        if stored_configs is None:
            self.logger.info('No backed up configuration packs present!!\nBackup folder is empty')
            return
        self.logger.info('These are the stored configs:')
        no_configs = len(stored_configs)
        for i in range(1,no_configs+1):
            self.logger.info('['+str(i)+'] '+stored_configs[i-1])

    def __get_source_paths(self):
        '''Get the list of configuration source paths from where we have to backup/copy configurations'''

        home_path = self.get_home_path()
        source_paths_file_location = self.get_value('config_list_path')
        source_paths = list()
        with open(source_paths_file_location, 'r') as source_paths_file:
            for source_path in source_paths_file:
                source_path = source_path.strip('\n')
                source_path = source_path.replace(' ','\ ')
                if (len(source_path) >= 2) & (not source_path.startswith('#')):
                    source_path = os.path.join(home_path, source_path)
                    source_paths.append(source_path)
                    self.logger.log(source_path)
        return source_paths

    def copy_configs_to_store(self, dest):
        '''Copy the current configurations mentioned into a store-configuration folder'''

        source_path_list = self.__get_source_paths()
        error_occurred = False
        for source_path in source_path_list:
            try:
                call(['cp', '-a', source_path, dest])
            except Exception as e:
                self.logger.info('Following error occurred:')
                self.logger.info(e)
                error_occurred = True
        return error_occurred


    def __bak_file_exists(self, source_paths):
        '''Checks if the backup exists for the source paths provided'''

        no_bk_list = list()
        for source_path in source_paths:
            source_path_bk = source_path + BAK_FILE_EXTENSION
            self.logger.log('checking for backup config '+ source_path_bk)
            exists = os.path.exists(source_path_bk)
            if not exists:
                no_bk_list.append(source_path)
        return no_bk_list

    def create_bak_file(self, ctx):
        '''Creates backup for the current source configurations for which no backup exists'''

        source_paths = self.__get_source_paths()
        no_bk_list = self.__bak_file_exists(source_paths)
        if len(no_bk_list) == 0:
            return

        any_error = False
        for source_path in no_bk_list:
            source_path_bk = source_path + BAK_FILE_EXTENSION
            self.logger.log('creating backup for '+source_path)
            exit_code = call(['mv', '-v', source_path, source_path_bk])
            if exit_code != 0:
                self.logger.info('Could not backup ' + source_path + ' to '+source_path_bk)
                any_error = True
        if any_error:
            self.logger.info('There was error creating backup for 1 or more configurations\nSo aborting....')
            ctx.abort()

    def copy_to_set_locations(self, ctx, stored_config_name):
        '''Copy the stored configuration to the specific locations'''

        default_locations = self.__get_source_paths()
        config_path = self.get_value('store_dir')
        source_path = os.path.join(config_path, stored_config_name)
        any_error = False
        src = [stored_config for stored_config in os.listdir(source_path)]
        for config in src:
            associated_path = self.__get_associated_path(config, default_locations)
            if associated_path is None:
                slef.logger.log('could not find associated path to apply '+config)
                self.logger.log('So skipping applying this config!!')
                continue
            source_location = os.path.join(source_path, config)
            self.logger.log('Applying '+source_location + ' to '+associated_path)
            error_code = call(['cp', '-a', source_location, associated_path])
            if error_code != 0:
                any_error = True
                self.logger.info('Issue copying '+source_location + ' into '+associated_path)
        if any_error:
            self.logger.info('Encountered error while applying 1 or more configurations....\nSo aborting')
            ctx.abort()


    def __get_associated_path(self, config, config_paths):
        for config_path in config_paths:
            if config in config_path:
                return config_path

    def delete_location(self, location):
        shutil.rmtree(location)

    def create_directory(self, location, overwrite=False):
        '''Creates directory at said location:
            return 1: if error occured while creating directory
                   0: if directory created successfully
                  -1: if directory already exists and overwrite flag was False'''

        if os.path.exists(location):
            self.logger.log('Folder at ' + location + ' already exists')
            if not overwrite:
                return -1, None
            else:
                self.delete_location(location)
        try:
            os.mkdir(location)
            return 0, None
        except Exception as error:
            return 1, error

class my_dict(dict):
    '''My own dictionary implementation to use dictionary both as a dict and like an object interchengably'''
    def __init__(self):
        self.__dict__ = self
