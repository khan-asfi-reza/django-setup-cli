import os
import random
import string
import click


def error(text, **kwargs):
    click.secho(text, fg="red", **kwargs)


def log(test, **kwargs):
    click.secho(test, fg="cyan", **kwargs)


def success(text, **kwargs):
    click.secho(text, fg="green", **kwargs)


def pip_name() -> str:
    # if platform.system() == "Linux" or platform.system() == "Darwin":
    #     return "pip3"
    return "pip3"


# Terminal Execution
def execute(terminal_command: str) -> None:
    os.system(terminal_command)


def create_secret_key():
    chars = string.ascii_letters + string.digits
    return "_" + "".join([random.choice(chars) for i in range(64)])
