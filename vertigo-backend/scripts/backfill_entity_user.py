import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.app import create_app, db
import sqlalchemy as sa

from api.models.series import Series
from api.models.series_entities import Publisher, Character, Creator, Genre

app = create_app()
app.app_context().push()

print("\n--- Starting user_id backfill from Series side ---\n")

# Only series that already have a user_id
series_items = db.session.scalars(
    sa.select(Series).where(Series.user_id != None)
).all()

print(f"Series with user_id: {len(series_items)}\n")

updated_counts = {
    "publisher": 0,
    "genre": 0,
    "creator": 0,
    "character": 0,
}

for s in series_items:
    uid = s.user_id

    # Series.publisher is lazy='dynamic' → a query, can iterate directly
    for pub in s.publisher:
        if pub.user_id is None:
            pub.user_id = uid
            updated_counts["publisher"] += 1

    for gen in s.genre:
        if gen.user_id is None:
            gen.user_id = uid
            updated_counts["genre"] += 1

    for cre in s.creator:
        if cre.user_id is None:
            cre.user_id = uid
            updated_counts["creator"] += 1

    for char in s.character:
        if char.user_id is None:
            char.user_id = uid
            updated_counts["character"] += 1

db.session.commit()

print("\n--- Backfill complete ---")
for k, v in updated_counts.items():
    print(f"{k}: {v} rows updated")
print()