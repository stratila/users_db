"""
Ref: https://stackoverflow.com/a/74875605
"""

from pathlib import Path

from alembic.config import Config
from alembic import command


ROOT_PATH = Path(__file__).parent.parent
ALEMBIC_CFG = Config(ROOT_PATH / "alembic.ini")


def current(verbose=False):
    command.current(ALEMBIC_CFG, verbose=verbose)


def upgrade(revision="head"):
    command.upgrade(ALEMBIC_CFG, revision)


def downgrade(revision):
    command.downgrade(ALEMBIC_CFG, revision)


def revision(autogenerate=False, message=None):
    command.revision(ALEMBIC_CFG, message=message, autogenerate=autogenerate)
