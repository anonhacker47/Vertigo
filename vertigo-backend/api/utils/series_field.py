from api.app import db
import api.models.series_entities as series_entities

def create_or_get_entities(entity_type, titles, description=None):
    if not titles:  # Check for empty or None list
        return []

    entity_class = {
        'publisher': series_entities.Publisher,
        'genre': series_entities.Genre,
        'creator': series_entities.Creator,
        'main_character': series_entities.MainCharacter,
    }[entity_type]

    entities = []
    for title in titles:
        if title:
            existing_entity = db.session.query(entity_class).filter_by(title=title).first()
            if existing_entity:
                entities.append(existing_entity)
            else:
                new_entity = entity_class(title=title, description=description)
                db.session.add(new_entity)
                db.session.commit()
                entities.append(new_entity)
    return entities