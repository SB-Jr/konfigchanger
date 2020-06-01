import click
import os
import shutil
import json
import konfchanger_utils as utils

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

    config_list_path = utils.check_and_return_defaults(ctx, 'config_list_path', config_list_path)
    utils.check_config_file(ctx, config_list_path)

    config_path = utils.check_and_return_defaults(ctx, 'config_path', config_path)
    if not os.path.isdir(config_path):
        click.echo('No backup folder found...\nCreating a backup folder at ' + config_path)
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
            click.confirm('Do you want to overwrite the exisiting configuration backup?', abort=True)
            shutil.rmtree(backup_location)
        os.mkdir(backup_location)
    except error:
        click.echo('Error creating backup folder at ' + backup_location)
        click.echo(error)
    else:
        click.echo(
            name + ' Backup complete, with the folder name as ' + fixed_name)



@konfchanger.command()
@click.option('--name')
@click.pass_context
def apply(ctx, name):
    '''Apply a backed-up configuration'''

    config_path, configs = utils.get_list_configs(ctx, None, False)
    if (name is not None) & (name not in configs):
        click.echo(name + ' provided doesnt match with any existing saved configurations.\n Please select one from below:\n')
    if not name or name not in configs:
        name = utils.get_config_name(configs)
    # send kwin reconfigure signal
    click.echo(name + ' ---- Applied')



@konfchanger.command()
@click.pass_context
def list(ctx):
    '''List all available backed up configurations'''
    utils.get_list_configs(ctx, None)



@konfchanger.command('delete')
@click.option('-n', '--name')
@click.pass_context
def delete_configuration_backup(ctx, name):
    '''Delete a backed-up configuration'''

    config_path, configs = utils.get_list_configs(ctx, None, False)
    if (name is not None) & (name not in configs):
        click.echo(name + ' provided doesnt match with any existing saved configurations.\n Please select 1 from below:\n')
    if not name or name not in configs:
        name = utils.get_config_name(configs)
    if click.confirm('Do you really want to delete '+ name + ' configuration?', abort=True):
        rem_config_path = os.path.join(utils.check_and_return_defaults(ctx, 'config_path', None), name)
        shutil.rmtree(rem_config_path)
        click.echo(name + ' configuration deleted!!')
