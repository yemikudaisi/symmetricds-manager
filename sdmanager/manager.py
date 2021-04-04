import configparser
import subprocess
from sdmanager.core import ReplicationBuilder
import click

config_parser = configparser.ConfigParser()
config_parser.sections()
config_parser.read('conf.ini')

@click.group()
def cli():
    """SymmetricDS Manager."""
    click.echo('SymmetricDS Manager')

@cli.command()
@click.option('-p', '--properties', required=True, help='Manager replication properties file.')
@click.option('-o', '--output', help='Symmetric DS files Output directory to save SymmetricDS files.')
def build(config, output=None):
    sd_home = None
    if 'SYMMETRICDS' in config_parser.sections():
        sd_home = config_parser['SYMMETRICDS']['HomeDirectory']
    print(f"Using SymmetricDS home at {sd_home}")
  
    builder = ReplicationBuilder(config, output)
    builder.generate_files();

@cli.command()  # @cli, not @click!
def run():
    print('Running command')
    result = subprocess.run(["dir", "/p"], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

@cli.command()
@click.argument('section', required=True)
def set_config(section: str) -> None:
    """gets a specific config value from INI file

    Args:
        section (str): Section hierarchy in INI file separate by dot ('.').
        Exampe: Section `foo.bar` will translate to the below in INI config
        [foo]
        bar = 'Hello Worl'
        
        $ > manager get-config foo.bar
        Hello World
    """
    sections = section.split('.')
    if sections[0] in config_parser.sections():
        value = config_parser[sections[0]][sections[1]]
    else:
        click.echo('Configuration not found')
    # TODO Exception check
    click.echo(value)

@cli.command()
@click.argument('key', required=True)
def get_config(key: str) -> None:
    """gets a specific config value from INI file

    Args:
        key (str): Compination of INI section and key separated by dot ('.').
        Exampe: Key `foo.bar` will translate to the below in INI config
        `conf.ini`
        [foo]
        bar = Hello World
        
        $ > manager get-config foo.bar
        OUTPUT: Hello World
    """
    sections = key.split('.')
    if (len(sections) != 2):
        click.echo("Comibation of INI section and key separated by '.' required.")
    elif not sections[0] in config_parser.sections():
        click.echo(f"INI section '{sections[0]}' does not exist.")
    elif not sections[1] in config_parser[sections[0]]:
        click.echo("INI key '{sections[1]}' not found in section '{sections[0]}'.")
    else:
        value = config_parser[sections[0]][sections[1]]
    # TODO Exception check if key exists
    click.echo(value)


