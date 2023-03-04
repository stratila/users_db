"""
Ref: https://stackoverflow.com/a/74875605
Also check [tool.poetry.scripts] in pyproject.toml
"""
import click
import users_db.migrations as migrations


@click.command()
@click.option("-v", "--verbose", is_flag=True, default=False, help="Verbose mode")
def db_current_cmd(verbose):
    """Display current database revision"""
    migrations.current(verbose)


@click.command()
@click.option("-r", "--revision", default="head", help="Revision target")
def db_upgrade_cmd(revision):
    """Upgrade to a later database revision"""
    migrations.upgrade(revision)


@click.command()
@click.option("-r", "--revision", required=True, help="Revision target")
def db_downgrade_cmd(revision):
    """Revert to a previous database revision"""
    migrations.downgrade(revision)
