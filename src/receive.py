from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.types.inline_keyboard import (InlineKeyboardButton,
                                           InlineKeyboardMarkup)

import src.config as config
from src.config import bot
from src.database import Database
from src.edadil import Edadil

ITEMS_LIMIT = 5


class UsersStates(StatesGroup):
    search_item = State()


class Receive:
    async def command_start(self, message: types.Message, state: FSMContext):
        db = Database()

        if state:
            await state.finish()

        if await db.users.get.ID(message.from_id) is None:
            await db.users.add(message.from_id)

            return await bot.send_message(
                chat_id=message.chat.id,
                text=config.TEXT['command_start'])

        return await self.command_sale(message, state)

    async def command_sale(self, message: types.Message, state: FSMContext):
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        buttons = []

        if state:
            await state.finish()

        for num, segment in enumerate(config.EDADIL_SEGMENTS):
            if not config.EDADIL_SEGMENTS_ITEMS[num]:
                continue

            buttons.append(
                InlineKeyboardButton(
                    text=segment['name'],
                    callback_data=f'sale_{num}'))

        inline_keyboard.add(*buttons)

        return await bot.send_message(
            chat_id=message.chat.id,
            text=config.TEXT['command_sale'],
            reply_markup=inline_keyboard)

    async def button_sale(self, call: types.CallbackQuery, state: FSMContext):
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        buttons = []

        if state:
            await state.finish()

        for num, segment in enumerate(config.EDADIL_SEGMENTS):
            buttons.append(
                InlineKeyboardButton(
                    text=segment['name'],
                    callback_data=f'sale_{num}'))

        inline_keyboard.add(*buttons)

        return await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=config.TEXT['command_sale'],
            reply_markup=inline_keyboard)

    async def button_sale_items(self, call: types.CallbackQuery, state: FSMContext):
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        segment_id = int(call.data.split('_')[-1])
        msg_text = ''

        if state:
            await state.finish()

        for item in config.EDADIL_SEGMENTS_ITEMS[segment_id][:ITEMS_LIMIT]:
            msg_text += f'{item["name"]}\n<s>{item["old_price"]} </s> {item["price"]} ₽ <b>-{item["sale_perc"]}%</b>\n{item["shop"]}\n\n'

        inline_keyboard.add(
            InlineKeyboardButton(
                text='« Назад',
                callback_data='sale'))

        return await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=msg_text,
            reply_markup=inline_keyboard)

    async def command_search(self, message: types.Message, state: FSMContext):
        if state:
            await state.finish()

        await UsersStates.search_item.set()

        return await bot.send_message(
            chat_id=message.chat.id,
            text=config.TEXT['command_search'])

    async def state_search(self, message: types.Message, state: FSMContext):
        await state.finish()

        edadil = Edadil()
        msg_text = ''

        await bot.send_message(
            chat_id=message.chat.id,
            text=config.TEXT['search_start'])

        items = await edadil.get_search_items(message.text)

        if not items:
            return await bot.send_message(
                chat_id=message.chat.id,
                text=config.TEXT['search_not_found'])

        for item in items[:ITEMS_LIMIT]:
            msg_text += f'{item["name"]}\n<s>{item["old_price"]} </s> {item["price"]} ₽ <b>-{item["sale_perc"]}%</b>\n{item["shop"]}\n\n'

        return await bot.send_message(
            chat_id=message.chat.id,
            text=msg_text)
