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

def get_list_configs(ctx, config_path):
    if not config_path:
        ctx.abort()
    elif not os.path.isdir(config_path):
        click.echo('Path '+ config_path+ ' is not a directory!!')
    else:
        click.echo('These are the backed up configurations available')
        configs =  [configs for configs in os.listdir(config_path)]
        for config in configs:
            click.echo('- [ ] ' + config)
        return configs
