import configparser
import subprocess
from core import ReplicationBuilder
import click

@click.group()
def cli():
    """SymmetricDS Manager."""
    click.echo('SymmetricDS Manager')

@cli.command()
@click.option('-c', '--config', required=True, help='Manager replication configuration files.')
@click.option('-o', '--output', help='Output directory to save SymmetricDS files.')
def main(confif, output=None):
    config = configparser.ConfigParser()
    config.sections()
    config.read('conf.ini')
    sd_home = None
    if 'SYMMETRICDS' in config.sections():
        sd_home = config['SYMMETRICDS']['HomeDirectory']
    print(f"Using SymmetricDS home at {sd_home}")
  
    builder = ReplicationBuilder(conf, output)
    builder.generate_files();

@cli.command()  # @cli, not @click!
def run():
    print('Running command')
    result = subprocess.run(["dir", "/p"], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)



