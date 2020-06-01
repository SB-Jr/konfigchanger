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
        click.echo('Config file Found!! \n value = ' + str(ctx.default_map))
    pass

@konfchanger.command()
@click.option('-c', '--config-path', 'config_path', type=click.Path())
@click.option('-cl', '--config-list-path', 'config_list_path', type=click.Path())
@click.option('--name', required=True, prompt='Please give a name to the current configuration backup!\nNOTE: Space in the name will be converted into "_"(underscore)')
@click.pass_context
def backup(ctx, config_path, config_list_path, name):
    '''Backup current configuration'''
    if not config_list_path:
        config_list_path = ctx.parent.default_map['config_list_path']
    check_config_file(ctx, config_list_path)

    if not config_path:
        config_path = ctx.parent.default_map['config_path']

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
    if not os.path.isfile(config_list_path):
        click.echo('Configuration List not provided, so nothing will be backed up.\n Please create a ' +
                   config_list_path + ' file or provide a new location using the "-cl" flag')
        ctx.abort()


# konfchanger.add_command(backup)
# konfchanger.add_command(apply)
# konfchanger.add_command(delete_configuration_backup)
# konfchanger.add_command(list)
