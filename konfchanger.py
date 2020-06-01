import click
import os
import shutil
import json

home_path = os.getenv('HOME')
config = '.konfchanger_default_config'


@click.group()
@click.pass_context
@click.option('-c', '--config', 'config', default=config, type=click.Path())
def konfchanger(ctx, config):
    '''This is a tool to backup/restore KDE configuration and styles.'''
    click.echo('Checking for config file')
    try:
        ctx.ensure_object(dict)
        with open(config, 'r') as cfg:
            ctx.default_map = json.load(cfg)
    except:
        click.echo('config file doesnt not exist at '+config+'\n Either add a config file or pass a <path-to-config-file> using "-c" or "--config" flag')
    else:
        click.echo('Config file Found!!')
    pass

@konfchanger.command()
@click.option('-c', '--config-path', 'config_path', type=click.Path())
@click.option('-cl', '--config-list-path', 'config_list_path', type=click.Path())
@click.option('--name', required=True, prompt='Please give a name to the current configuration backup!\nNOTE: Space in the name will be converted into "_"(underscore)')
@click.pass_context
def backup(ctx, config_path, config_list_path, name):
    '''Backup current configuration'''

    config_list_path = check_and_return_defaults(ctx, 'config_list_path', config_list_path)
    check_config_file(ctx, config_list_path)

    config_path = check_and_return_defaults(ctx, 'config_path', config_path)
    if not os.path.isdir(config_path):
        click.echo(
            'No backup folder found...\nCreating a backup folder at ' + config_path)
        try:
            os.mkdir(config_path)
        except error:
            click.echo(
                'Could not create directory for config backup at ' + config_path)
            click.echo(error)
            return
    fixed_name = name.replace(' ', '_')
    backup_location = os.path.join(config_path, fixed_name)
    configuration_exists = False
    if os.path.isdir(backup_location):
        click.echo('configuration backup with this name already exists')
        configuration_exists = True
    try:
        if configuration_exists:
            click.confirm(
                'Do you want to overwrite the exisiting configuration backup?', abort=True)
            shutil.rmtree(backup_location)
        os.mkdir(backup_location)
    except error:
        click.echo('Error creating backup folder at ' + backup_location)
        click.echo(error)
    else:
        click.echo(
            name + ' Backup complete, with the folder name as ' + fixed_name)


@konfchanger.command()
@click.option('--name', required=True, prompt='Please enter the name of the configuration that you want to apply')
def apply(name):
    '''Apply a backed-up configuration'''
    # send kwin reconfigure signal
    click.echo(name + ' ---- Applied')


@konfchanger.command()
def list():
    '''List all available backed up configurations'''
    click.echo('These are the backed up configurations available')


@konfchanger.command()
@click.confirmation_option()
def delete_configuration_backup():
    '''Delete a backed-up configuration'''
    click.echo('configuration deleted')


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
