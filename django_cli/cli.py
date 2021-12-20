import click
from dotenv import load_dotenv

from django_cli.const import DEFAULT_ENV_FILE
from django_cli.setup_project.handler import ProjectInitializer
import os

from django_cli.utils import error


@click.group()
def cli():
    """Django Cli"""


def load_cli_env(env):
    try:
        load_dotenv(dotenv_path=f"{os.getcwd()}/{env}")
    except FileNotFoundError:
        if env != DEFAULT_ENV_FILE:
            error("Invalid env file")


@cli.command('generate', help="Generates YAML File")
@click.option("--env", 'env', default=DEFAULT_ENV_FILE, help="Target Environment File")
@click.argument('name', required=False)
def make_generate(name, env):
    load_cli_env(env)
    ProjectInitializer(project_name=name).generate()


@cli.command('startproject', help="Starts Django Project")
@click.option("--env", 'env', default=DEFAULT_ENV_FILE, help="Target Environment File")
@click.argument('name', required=False)
def start_project(name, env):
    load_cli_env(env)
    ProjectInitializer(project_name=name).start_project()


@cli.command('install', help="Install Libraries that are in setup.yaml and requirements file")
@click.option("--env", 'env', default=DEFAULT_ENV_FILE, help="Target Environment File")
def install_libraries(env):
    load_cli_env(env)
    load_dotenv()
    ProjectInitializer().install_libraries()
