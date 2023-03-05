import os
import click
import contextlib

import users_db
from users_db import migrations

# We need to change the current working directory to the path where
# users_db is installed.
USERS_DB_ABSPATH = os.path.dirname(os.path.abspath(users_db.__file__))


@contextlib.contextmanager
def cd(new_dir):
    """This is a context manager that changes the current working directory"""
    prev_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)


# The idea to use Click module seen in https://stackoverflow.com/a/74875605


@click.command()
@click.option("-v", "--verbose", is_flag=True, default=False, help="Verbose mode")
def db_current_cmd(verbose):
    """Display current database revision"""
    with cd(USERS_DB_ABSPATH):
        migrations.current(verbose)


@click.command()
@click.option("-r", "--revision", default="head", help="Revision target")
def db_upgrade_cmd(revision):
    """Upgrade to a later database revision"""
    with cd(USERS_DB_ABSPATH):
        migrations.upgrade(revision)


@click.command()
@click.option("-r", "--revision", required=True, help="Revision target")
def db_downgrade_cmd(revision):
    """Revert to a previous database revision"""
    with cd(USERS_DB_ABSPATH):
        migrations.downgrade(revision)