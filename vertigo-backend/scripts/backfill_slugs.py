import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.app import create_app, db
from slugify import slugify
import sqlalchemy as sa

app = create_app()
app.app_context().push()

from api.models.series_entities import Publisher
from api.models.series_entities import Character
from api.models.series_entities import Creator
from api.models.series_entities import Genre

models = [Publisher, Character, Creator, Genre]

for model in models:
    stmt = sa.select(model).where(
        sa.or_(model.slug == None, model.slug == "")
    )
    items = db.session.execute(stmt).scalars().all()

    print(f"Updating {model.__tablename__}: {len(items)} rows")

    for item in items:
        item.slug = slugify(item.title)

    db.session.commit()

print("\nDone! Slug fields updated.\n")
