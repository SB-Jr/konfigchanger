import os
import click

def check_config_file(ctx, config_list_path):
    '''Checks the presence of config file to use in the cli'''

    if not os.path.isfile(config_list_path):
        click.echo('Configuration List not provided, so nothing will be backed up.\n Please create a ' +
                   config_list_path + ' file or provide a new location using the "-cl" flag')
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

def get_list_configs(ctx, config_path, print_configs=True):
    '''Gets the list of configurations from store folder
       If no store folder is provided then it fetches the
       default folder and then get the list of configurations'''

    config_passed = True
    if config_path is None:
        config_path = check_and_return_defaults(ctx, 'config_path', None)
        config_passed = False

    if not os.path.isdir(config_path):
        click.echo('Path '+ config_path+ ' is not a directory!!')
    else:
        click.echo('These are the backed up configurations available')
        configs =  [configs for configs in os.listdir(config_path)]
        if print_configs:
            echo_configs(configs)
        if config_passed:
            return configs
        else:
            return config_path, configs

def get_config_name(configs):
    '''Gives user a list of available configs and lets them chose one from the list'''

    no_configs = len(configs)
    echo_configs(configs)
    value = click.prompt('Please enter the number associated with the configuration, you want to delete:', type=click.IntRange(1, no_configs))
    name = configs[value - 1]
    return name

def echo_configs(configs):
    no_configs = len(configs)
    for i in range(1,no_configs+1):
        click.echo('['+str(i)+'] '+configs[i-1])
