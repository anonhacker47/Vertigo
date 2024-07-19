from api.app import db
from api.models.series_entities import *

def create_or_get_entities(entity_type, titles, description=None):
    if titles is None:
        return []

    entity_class = {
        'publisher': Publisher,
        'genre': Genre,
        'team': Team,
        'writer': Writer,
        'editor': Editor,
        'artist': Artist,
        'inker': Inker,
        'colorist': Colorist,
        'character': Character,
        'penciller': Penciller,
        'letterer': Letterer
    }[entity_type]

    entities = []
    for title in titles:
        existing_entity = db.session.query(entity_class).filter_by(title=title).first()
        if existing_entity:
            entities.append(existing_entity)
        else:
            new_entity = entity_class(title=title, description=description)
            db.session.add(new_entity)
            db.session.commit()
            entities.append(new_entity)
    return entities


def create_or_get_main_character(main_char_type, main_char_title):
    if main_char_type == 'character':
        entity_class = Character
    elif main_char_type == 'team':
        entity_class = Team
    else:
        raise ValueError("Invalid main_char_type. Must be 'character' or 'team'.")

    existing_entity = db.session.query(entity_class).filter_by(title=main_char_title).first()
    if existing_entity:
        return existing_entity
    else:
        new_entity = entity_class(title=main_char_title)
        db.session.add(new_entity)
        db.session.commit()
        return new_entity