import os
import click
from subprocess import call

def get_home_path():
    home_path = os.getenv('HOME')
    return home_path

def get_current_directory():
    current_path = os.getcwd()
    return current_path

def check_config_file(ctx, config_list_path):
    '''Checks the presence of config file to use in the cli'''

    if not os.path.isfile(config_list_path):
        click.echo('Configuration List not provided, so nothing will be backed up.\n Please create a ' +
                   config_list_path + ' file')# or provide a new location using the "-cl" flag')
        ctx.abort()

def check_and_return_defaults(ctx, key, value):
    '''Checks if value is valid, if not then returns the default value from context object'''

    if value:   #value is valid
        return value
    if not ctx: #if context is not valid we cant find default value
        return None
    elif not ctx.default_map: # if default value not present in current context then check parent context recursively
        return check_and_return_defaults(ctx.parent, key, value)
    else: #value is in the current context object
        return ctx.default_map[key]

def get_value(ctx, key):
    '''Retrives the value associated with the key from context object'''
    if ctx is None: #if context is not valid we cant find default value
        return None
    elif ctx.default_map is None: # if default value not present in current context then check parent context recursively
        return get_value(ctx.parent, key)
    else: #value is in the current context object
        return ctx.default_map[key]

def get_list_configs(ctx, config_path, print_configs=True):
    '''Gets the list of stored configurations from store folder
       If no store folder is provided then it fetches the
       default store folder and then get the list of stored configurations'''

    config_passed = True
    if config_path is None:
        config_path = get_value(ctx, 'config_path')
        config_passed = False

    if not os.path.isdir(config_path):
        click.echo('Path '+ config_path+ ' is not a directory!!')
        ctx.abort()
    else:
        configs = [config for config in os.listdir(config_path)]
        if len(configs) == 0:
            click.echo('No backed up configs present')
        else:
            if print_configs:
                echo_configs(configs)
            if config_passed:
                return configs
            else:
                return config_path, configs

def get_config_name(configs):
    '''Gives user the list of stored configs prvided in parameter and lets them choose one from the list'''

    no_configs = len(configs)
    echo_configs(configs)
    value = click.prompt('Please enter the number associated with the configuration, you want to delete:', type=click.IntRange(1, no_configs))
    name = configs[value - 1]
    return name

def echo_configs(configs):
    '''Prints the stored config list passed'''
    click.echo('These are the stored configs:')
    no_configs = len(configs)
    for i in range(1,no_configs+1):
        click.echo('['+str(i)+'] '+configs[i-1])

def __get_source_paths(ctx):
    '''Get the list of configuration source paths from where we have to backup/copy configurations'''
    home_path = get_home_path()
    source_paths_file_location = get_value(ctx, 'config_list_path')
    source_paths = list()
    with open(source_paths_file_location, 'r') as source_paths_file:
        for source_path in source_paths_file:
            source_path = source_path.strip('\n')
            source_path = source_path.replace(' ','\ ')
            if (len(source_path) >= 2) & (not source_path.startswith('#')):
                source_path = os.path.join(home_path, source_path)
                source_paths.append(source_path)
                click.echo(source_path)
    return source_paths

def copy_configs(ctx, dest):
    '''Copy the current configurations mentioned into a store-configuration folder'''
    source_path_list = __get_source_paths(ctx)
    for source_path in source_path_list:
        try:
            call(['cp', '-a', source_path, dest])
        except Exception as e:
            click.echo('Following error occurred:')
            click.echo(e)
            ctx.abort()

def __backup_exists(ctx, source_paths):
    '''Checks if the backup exists for the source paths provided'''
    no_bk_list = list()
    for source_path in source_paths:
        source_path_bk = source_path + '.bk'
        click.echo('checking for backup config '+ source_path_bk)
        exit_code = call(['ls', '-al', source_path_bk ])
        if exit_code != 0:
            no_bk_list.append(source_path)
    return no_bk_list

def create_backup(ctx):
    '''Creates backup for the source configurations for which no backup exists'''
    source_paths = __get_source_paths(ctx)
    no_bk_list = __backup_exists(ctx, source_paths)
    if len(no_bk_list) == 0:
        return

    any_error = False
    for source_path in no_bk_list:
        source_path_bk = source_path + '.bk'
        click.echo('creating backup for '+source_path)
        exit_code = call(['mv', '-v', source_path, source_path_bk])
        if exit_code != 0:
            click.echo('Could not backup ' + source_path + ' to '+source_path_bk)
            any_error = True
    if any_error:
        click.echo('There was error creating backup for 1 or more configurations\nSo aborting....')
        ctx.abort()

def copy(ctx, stored_config_name):
    '''Copy the stored configuration to the specific locations'''
    default_locations = __get_source_paths(ctx)
    config_path = get_value(ctx, 'config_path')
    source_path = os.path.join(config_path, stored_config_name)
    any_error = False
    src = [stored_config for stored_config in os.listdir(source_path)]
    for config in src:
        associated_path = __get_associated_path(config, default_locations)
        if associated_path is None:
            click.echo('could not find associated path to apply '+config)
            click.echo('So skipping applying this config!!')
            continue
        source_location = os.path.join(source_path, config)
        click.echo('Applying '+source_location + ' to '+associated_path)
        error_code = call(['cp', '-a', source_location, associated_path])
        if error_code != 0:
            any_error = True
            click.echo('Issue copying '+source_location + ' into '+associated_path)
    if any_error:
        click.echo('Encountered error while applying 1 or more configurations....\nSo aborting')
        ctx.abort()


def __get_associated_path(config, config_paths):
    for config_path in config_paths:
        if config in config_path:
            return config_path
