import json
import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from src.database import Database

BOT_TOKEN = ''

TEXT: json
EDADIL_SEGMENTS: list
EDADIL_SEGMENTS_ITEMS: list

bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


class BotStartupLoad:
    """
    Base class to load at startup
    """
    async def json_files(self):
        """
        Use this method to load json files
        """
        global TEXT, EDADIL_SEGMENTS, EDADIL_SEGMENTS_ITEMS

        EDADIL_SEGMENTS = []
        EDADIL_SEGMENTS_ITEMS = []

        if not os.path.exists('data/json/text.json'):
            with open(f'data/json/text.json', 'w', encoding='utf-8') as text_file:
                json.dump(obj={}, fp=text_file, ensure_ascii=False, indent=4)

        with open('data/json/text.json', 'r', encoding='utf-8') as text_file:
            TEXT = json.load(text_file)


class BotStartupCreate:
    """
    Base class to create at startup
    """
    async def dirs(self):
        """
        Use this method to create non-existent
        directories.
        """
        if not os.path.exists('data'):
            os.mkdir('data')

        if not os.path.exists('data/json'):
            os.mkdir('data/json')

        if not os.path.exists('db'):
            os.mkdir('db')


class BotStartup:
    """
    Base bot startup class
    """
    startupLoad = BotStartupLoad()
    startupCreate = BotStartupCreate()
    database = Database()

    async def start(self):
        """
        Use this method at bot startup to
        create and load.
        """
        await self.__create()
        await self.__load()

    async def __load(self):
        """
        Use this method at bot startup to load
        """
        await BotStartup.startupLoad.json_files()

    async def __create(self):
        """
        Use this method at bot startup to create
        """
        await BotStartup.startupCreate.dirs()
        await BotStartup.database.create()
