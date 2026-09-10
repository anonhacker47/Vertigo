import click
from api import create_app

app = create_app()

@app.cli.group()
def db():
    """Database commands."""
    pass

@db.command()
def upgrade():
    """Create or upgrade the database."""
    from alembic.config import main
    main(argv=['upgrade', 'head'])


@app.cli.group()
def media():
    """Image storage commands."""
    pass

@media.command("migrate")
@click.option("--dry-run", is_flag=True, help="Report what would move without changing anything.")
@click.option("--purge-orphans", is_flag=True,
              help="Also delete legacy image files that no database row references.")
def media_migrate(dry_run, purge_orphans):
    """Move images from Config/User/<id>/... into the users/<id>/ layout and rewrite DB paths."""
    from api.media_migrate import migrate_media
    migrate_media(dry_run=dry_run, purge_orphans=purge_orphans, log=click.echo)
