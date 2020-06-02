import click
import os
from konfchanger_utils import Utils

utils = Utils()

@click.group()
@click.pass_context
def konfchanger(ctx):
    '''This is a tool to backup/restore KDE configuration and styles.'''

    if utils is None:
        ctx.abort()
    utils.logger.log('Checking for Backup directory')
    store_present = utils.is_store_dir_present()
    if (ctx.invoked_subcommand != 'init') and (not store_present):
        utils.logger.info('Please run "init" command for the first time using this tool')
        ctx.abort()


@konfchanger.command('init')
@click.option('-v', '--verbose', is_flag=True,  callback=utils.enable_verbose)
@click.pass_context
def init_konfigchanger(ctx, verbose):
    config_list_path = utils.get_config_list_path()
    store_dir = utils.get_store_dir()
    error_code, error = utils.create_directory(store_dir)
    if error_code == -1:
        utils.logger.info('Backup folder already exists at ' + store_dir)
        utils.logger.info('You are good to go. Dont need to run init command again')
    elif error_code == 1:
        utils.logger.info('Could not create directory for config backup at ' + store_dir)
        utils.logger.info(e)
    else:
        utils.logger.log('Backup folder created successfully')


@konfchanger.command()
@click.option('-v', '--verbose', is_flag=True,  callback=utils.enable_verbose)
@click.option('--name')
@click.pass_context
def backup(ctx, name, verbose):
    '''Backup current configuration'''

    if not utils.is_config_list_path_present():
        ctx.abort()
    if name is None:
        name = click.prompt('Please give a name to the current configuration backup!\nNOTE: <Spaces> in the name will be converted into "_"(underscore)', type=click.STRING)
    fixed_name = name.replace(' ', '_')
    configuration_exists = utils.is_duplicate_name_present(fixed_name)
    absolute_path = utils.get_config_backup_absolute_path_by_name(fixed_name)
    overwrite = False
    if configuration_exists:
        overwrite = click.confirm('Do you want to overwrite the exisiting configuration backup?', abort=True)
        #utils.delete_location(absolute_path)
        utils.logger.log(str(overwrite))
        if not overwrite:
            ctx.abort()
    error_code, error = utils.create_directory(absolute_path, overwrite)
    if error_code == 0:
        if utils.copy_configs_to_store(absolute_path):
            utils.logger.info('Some error occurred while backing up your configurations.')
            utils.logger.info('Please use the delete command to delete this configurations backup if needed')
        else:
            utils.logger.info(name + ' Backup complete, You can apply this configuration by passing this name -> ' + fixed_name + ' with the --name flag for "apply" option')
    elif error_code == 1:
        utils.logger.info('Error creating backup folder at ' + absolute_path)
        utils.logger.info(error)




@konfchanger.command()
@click.option('-v', '--verbose', is_flag=True, callback=utils.enable_verbose)
@click.option('--name')
@click.pass_context
def apply(ctx, name, verbose):
    '''Apply a backed-up configuration'''

    stored_configs = utils.get_stored_configs()
    if stored_configs is None:
        utils.logger.info('No backed up configuration packs present!!\nBackup folder is empty')
        return
    if stored_configs is None:
        ctx.abort()
    if len(stored_configs) == 1:
        utils.logger.info('Only 1 configuration pack found!!')
        name = stored_configs[0]
        if not click.confirm('Do you want to apply '+ name + ' configuration pack?'):
            ctx.abort()
    else:
        if (name is not None) and (name not in stored_configs):# if wrong name is provided
            utils.logger.info(name + ' provided name doesnt match with any existing stored configurations.\n Please select one from below:\n')
        if (name is None) or (name not in stored_configs): #if no name is provided or wrong name is provided
            name = utils.get_config_name()
    utils.create_bak_file(ctx)
    utils.copy_to_set_locations(ctx, name)
    # send kwin reconfigure signal
    utils.logger.info(name + ' ---- Applied')



@konfchanger.command()
@click.option('-v', '--verbose', is_flag=True, callback=utils.enable_verbose)
@click.pass_context
def list(ctx, verbose):
    '''List all available backed up configurations'''
    utils.logger.log('Listing existing configurations')
    utils.get_stored_configs()
    utils.echo_configs()


#@click.option('-y','--yes')
@konfchanger.command('delete')
@click.option('-n', '--name')
@click.option('-v', '--verbose', is_flag=True,  callback=utils.enable_verbose)
@click.pass_context
def delete_configuration_backup(ctx, name, verbose):
    '''Delete a backed-up configuration'''

    stored_configs = utils.get_stored_configs()
    if stored_configs is None:
        utils.logger.info('No backed up configuration packs present!!\nBackup folder is empty')
        return
    if (name is not None) and (name not in stored_configs): # if wrong name is provided
        utils.logger.info(name + ' provided name doesnt match with any existing saved configurations.\n Please select 1 from below:\n')
    if (name is None) or (name not in stored_configs): # if no name is provided or wrong name is provided
        name = utils.get_config_name()
    if click.confirm('Do you really want to delete '+ name + ' configuration?', abort=True):
        rem_config_path = utils.get_config_backup_absolute_path_by_name(name)
        utils.delete_location(rem_config_path)
        utils.logger.info(name + ' configuration deleted!!')
