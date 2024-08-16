from src.models import Base, engine
from src.config import Config

import src.models.user
import src.models.token
import src.models.chat
import src.models.faq
import src.models.resource


def create_tables():
    Base.metadata.create_all(engine)


def drop_tables():
    if not Config.DEBUG:
        raise Exception("This script is only available in debug mode")
    Base.metadata.drop_all(engine)
