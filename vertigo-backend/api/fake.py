import random
import click
from flask import Blueprint
from faker import Faker
from api.app import db
from api.models.user import User
from api.models.series import Series
from slugify import slugify
from datetime import timezone,datetime
from api.models.issue import Issue
import api.models.series_entities as entities
import api.models.associations as associations
from api.helpers.thumbnail_processing import download_series_thumbnail

import mokkari

# session = Comicvine(api_key="97a8bbaedc58ef0da64b3a154c34016c71a8d188", cache=SQLiteCache())
session = mokkari.api("anonhacker47", "a62wCm9WuZjSVww")

comic_names = [
    "Watchmen",
    "The Dark Knight Returns",
    "Saga",
    "The Sandman",
    "Maus",
    "Y: The Last Man",
    "V for Vendetta",
    "Preacher",
    "Hellboy",
    "Sin City",
    "100 Bullets",
    "Fables",
    "Transmetropolitan",
    "The Walking Dead",
    "Locke & Key",
    "Bone",
    "Astro City",
    "Powers",
    "Strangers in Paradise",
    "Invisible",
    "The Authority",
    "Black Hole",
    "Love and Rockets",
    "The Invisibles",
    "Planetary",
    "American Vampire",
    "Criminal",
    "DMZ",
    "Scalped",
    "Sweet Tooth",
    "Chew",
    "Ex Machina",
    "Fatale",
    "Hitman Garth Ennis",
    "The Boys",
    "Hitman",
    "The Punisher MAX",
    "Judge Dredd",
    "Concrete",
    "The Maxx",
    "Ghost World",
    "Persepolis",
    "From Hell",
    "Black Science",
    "East of West",
    "Sex Criminals",
    "The Wicked + The Divine",
    "Monstress",
    "Paper Girls",
    "Lazarus",
    "Revival",
    "Outcast",
    "Nailbiter",
    "Deadly Class",
    "Wytches",
    "The Fade Out",
    "Descender",
    "Tokyo Ghost",
    "Deadman",
    "Redlands",
    "Black Magick",
    "Kill or Be Killed",
    "The Fix",
    "The Goddamned",
    "Deadly Class",
    "Criminal",
    "Incognito",
    "The Fade Out",
    "Fatale",
    "Gotham Central",
    "Scarlet",
    "Daredevil",
    "Immortal Hulk",
    "Moon Knight",
    "Hawkeye",
    "Ms. Marvel",
    "Captain Marvel",
    "Black Panther",
    "Doctor Strange",
    "Silver Surfer",
    "Guardians of the Galaxy",
    "Fantastic Four",
    "X-Men",
    "Uncanny X-Men",
    "X-Force",
    "New Mutants",
    "Wolverine",
    "Deadpool",
    "Nightcrawler",
    "Saga",
    "Bone",
    "The Walking Dead",
    "Y: The Last Man",
    "Sex Criminals",
    "Locke & Key",
    "Paper Girls",
    "Chew",
    "Black Hammer",
    "East of West",
    "Monstress",
    "Invincible",
    "Descender",
    "The Wicked + The Divine",
    "Saga of the Swamp Thing",
    "Sweet Tooth",
    "Preacher",
    "Sandman",
    "Fables",
    "Lobo",
]

datetime_start = datetime.strptime("2020-01-01", "%Y-%m-%d")
datetime_end = datetime.strptime("2024-07-31", "%Y-%m-%d")

publishers = [
    "DC Comics",
    "Marvel Comics",
    "Image Comics",
    "Dark Horse Comics",
    "IDW Publishing",
    "BOOM! Studios",
    "Valiant Entertainment",
    "Oni Press",
    "Archie Comics",
    "Dynamite Entertainment",
    "Titan Comics",
]

def get_comicid():
    filter_string = f"isssue_name:{random.choice(comic_names)}"
    print("enetered")
    comic_results = session.series_list({"filter": filter_string})
    print(comic_results)
    return comic_results

def get_comic_vine_info(title):
    # volume = session.list_volumes(params={"filter": f"name:{title}"}, max_results=1)[0].id
    try:
        volume = session.issue(title)
        return volume
    except Exception as e:
        print(f"Error fetching comicvine info: {e}")
        return None
    # for volume in results:    
    #     return {
    #         "id": volume.id,
    #         "image": volume.image.medium_url,
    #         "description": volume.description,
    #         "publisher": volume.publisher.name,
    #     }

fake = Blueprint('fake', __name__)
faker = Faker()

def create_or_get_entity(model, title):
    if isinstance(title, list):
        return [create_or_get_entity(model, t) for t in title]
    entity = db.session.query(model).filter_by(title=title).first()
    if entity is None:
        entity = model(title=title)
        db.session.add(entity)
    return entity


@fake.cli.command()
@click.argument('num', type=int)
def users(num):  # pragma: no cover
    """Create the given number of fake users."""
    for _ in range(num):
        user = User(username=faker.user_name(), email=faker.email())
        db.session.add(user)
    db.session.commit()
    print(num, 'users added.')

@fake.cli.command()
@click.argument('num', type=int)
def series(num):  # pragma: no cover
    """Create the given number of fake series."""
    users = db.session.scalars(User.select()).all()
    for _ in range(num):
        # comic_list = get_comicid()
        user = random.choice(users)
        volume = get_comic_vine_info(random.randint(1, 100000))
        if volume: 
            print(volume.id,volume.series.name)# Check if the list is not empty
        else:
            # comic_list = get_comicid()
            ("no volume found")
            volume = get_comic_vine_info(random.randint(1, 100000))
        title=volume.series.name
        image = volume.image.__str__()
        print(image)
        thumbnail_location,dominant_color = download_series_thumbnail(image, title)

        series = Series(
            title=title,
            user=user,
            user_rating=random.uniform(0, 5),
            description=volume.desc,
            manga=faker.boolean(),
            release_date=volume.cover_date,
            series_format=random.choice(['Hard Cover', 'Trade Paperback', 'Box Set', 'Omnibus', 'Absolute Edition', 'Single Issue','Graphic Novel']),
            slug=slugify(title),
            thumbnail=thumbnail_location,
            dominant_color=dominant_color,
            timestamp=faker.date_time_this_year(tzinfo=timezone.utc)
        )

        # Add relationships
        for entity_name, entity_model in {
            'publisher': entities.Publisher,
            'genre': entities.Genre,
            'creator': entities.Creator,
            'character': entities.Character,
            'team': entities.Team,
        }.items():
            if random.choice([True, False]):
                entity_titles = [str(c.name) for c in volume.series.genres] if entity_name == 'genre' else [str(c.creator) for c in volume.credits]
                entity_title = faker.text(max_nb_chars=20)
                if entity_name == 'publisher':
                    entity_titles = [volume.publisher.name]
                    entity = create_or_get_entity(entity_model, title)
                    getattr(series, entity_name).append(entity)
                if entity_name in ['genre', 'creator']:
                    for title in entity_titles:
                        entity = create_or_get_entity(entity_model, title)
                        getattr(series, entity_name).append(entity)
                else:
                    entity_title = faker.text(max_nb_chars=20)
                    entity = create_or_get_entity(entity_model, entity_title)
                    getattr(series, entity_name).append(entity)
                entity = create_or_get_entity(entity_model, entity_title)
                getattr(series, entity_name).append(entity)
        db.session.add(series)
    db.session.commit()
    print(num, 'series added.')


@fake.cli.command()
@click.argument('num', type=int)
def issues(num):  # pragma: no cover
    """Create the given number of fake issues, assigned to random series."""
    series_list = db.session.scalars(Series.select()).all()
    issue_count_by_series = {}
    issue_num = 0
    title = "volume"

    for _ in range(num):
        series = random.choice(series_list)
        user = series.user
        issue_num += 1
        issue = Issue(
            number=issue_num,
            title = f"volume {issue_num}",
            summary=faker.text(max_nb_chars=250),
            slug=slugify(title),
            is_read=faker.boolean(),
            is_owned=faker.boolean(),
            bought_date=faker.date_time_this_year(),
            read_date=faker.date_time_this_year(),
            timestamp=faker.date_time_this_year(tzinfo=timezone.utc),
            series=series,
            user=user
        )
        db.session.add(issue)

        # Track issue count for the series
        if series in issue_count_by_series:
            issue_count_by_series[series] += 1
        else:
            issue_count_by_series[series] = 1

    # Update issue_count for each series
    for series, count in issue_count_by_series.items():
        series.issue_count = count
        series.read_count=random.uniform(0, series.issue_count)
        series.owned_count=random.uniform(0, series.issue_count)

    db.session.commit()
    print(num, 'issues added.')