import asyncio

import aioschedule
from aiogram import executor, types
from aiogram.dispatcher import Dispatcher, filters

from src.config import BotStartup, dp
from src.edadil import Edadil
from src.receive import Receive, UsersStates
from src.schedule import Schedule

ALL_STATES = (UsersStates.search_item,)


async def bot_startup(dp: Dispatcher):
    """
    Use this method when starting the bot for initial setup
    """
    prepare = BotStartup()
    receive = Receive()
    edadil = Edadil()

    # bot prepare
    await prepare.start()

    print('Загрузка данных с сайта Едадил...')
    await edadil.update()
    print(f'Загрузка данных с сайта Едадил завершена!')

    # commands
    dp.register_message_handler(receive.command_start, filters.ChatTypeFilter(
        types.ChatType.PRIVATE), commands=['start'], state=(*ALL_STATES, None))

    dp.register_message_handler(receive.command_sale, filters.ChatTypeFilter(
        types.ChatType.PRIVATE), commands=['sale'], state=(*ALL_STATES, None))

    dp.register_message_handler(receive.command_search, filters.ChatTypeFilter(
        types.ChatType.PRIVATE), commands=['search'], state=(*ALL_STATES, None))

    # buttons
    dp.register_callback_query_handler(
        receive.button_sale, lambda call: (call.data == 'sale' and filters.ChatTypeFilter(
            types.ChatType.PRIVATE)), state=(*ALL_STATES, None))

    dp.register_callback_query_handler(
        receive.button_sale_items, lambda call: (call.data.startswith('sale_') and filters.ChatTypeFilter(
            types.ChatType.PRIVATE)), state=(*ALL_STATES, None))

    # states
    dp.register_message_handler(receive.state_search, filters.ChatTypeFilter(
        types.ChatType.PRIVATE), state=UsersStates.search_item)

    await dp.bot.set_my_commands([
        types.BotCommand('sale', 'Лучшие скидки'),
        types.BotCommand('search', 'Поиск по названию')])

    # aioschedule
    asyncio.create_task(start_aioschedule())


async def start_aioschedule():
    schedule_events = Schedule()

    aioschedule.every().hour.do(schedule_events.update_edadil)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


def main():
    executor.start_polling(dispatcher=dp, on_startup=bot_startup)


if __name__ == '__main__':
    main()
