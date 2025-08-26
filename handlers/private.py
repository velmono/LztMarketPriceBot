from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ChatType
from aiogram.types import (
    Message, 
    KeyboardButton,
    ReplyKeyboardMarkup
)
from aiogram.filters import Command
from services.links_service import create_report
from database.repositories.users import add, check_user, change_share


router = Router()
router.message.filter(F.chat.type.in_([ChatType.PRIVATE]))


class States(StatesGroup):
    CheckState = State()
    PercentState = State()


@router.message(Command("start", prefix="/!"))
async def start_message(message: Message, state: FSMContext):
    
    links_button = KeyboardButton(text="Проверить ссылки")
    config_button = KeyboardButton(text="Конфигурация")
    
    keyboard = ReplyKeyboardMarkup(keyboard=[[links_button,config_button]],resize_keyboard=True)
    
    if message.from_user is not None:
        await add(message.from_user.id) if not await check_user(message.from_user.id) else None
    answer_text = """Бот для проверки стоимости товаров на LZT MARKET.

Функционал:
Проверка ссылок - по ссылкам узнать стоимость и долю аккаунтов
Конфигурация - настройка вашего процента от суммы аккаунтов

"""
    await message.answer(text=answer_text,
                     reply_markup=keyboard
                     )


@router.message(F.text == "Отменить")
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_operation(message: Message, state: FSMContext):
    if await state.get_state() is None:
        await start_message(message, state)
    await state.clear()
    await message.answer("Отменено")
    await start_message(message, state)


@router.message(F.text == "Проверить ссылки")
async def answer_links(message: Message, state: FSMContext):
    
    cancel_button = KeyboardButton(text="Отменить")
    keyboard = ReplyKeyboardMarkup(keyboard=[[cancel_button]],resize_keyboard=True)
    
    
    await state.set_state(States.CheckState)
    
    answer_text = """💾Отправьте ссылки/ID
(Каждая ссылка/каждый ID с новой строки)

"""
    await message.answer(text=answer_text,
                         reply_markup=keyboard)


@router.message(States.CheckState)
async def check_links(message: Message, state: FSMContext):
    if message.text is not None:
        links = message.text.split()
        await message.answer(f"Ожидайте ссылки проверяются.\nЗаймет примерно {len(links)*0.5} секунд.")
        user_id = message.from_user.id if message.from_user is not None else 0
        await message.answer(f"Готово ваш отчет:\n{await create_report(links, user_id)}", disable_web_page_preview=True)
        await state.clear()
        await start_message(message, state)
    else:
        await message.answer("Отправьте ссылки корректно")
        await state.set_state(States.CheckState)


@router.message(F.text == "Конфигурация")
async def configure(message: Message, state: FSMContext):
    cancel_button = KeyboardButton(text="Отменить")
    keyboard = ReplyKeyboardMarkup(keyboard=[[cancel_button]],resize_keyboard=True)
    
    await state.set_state(States.PercentState)
    await message.answer("Отправь Ваш процент от всей суммы(Например: 20)",
                         reply_markup=keyboard)


@router.message(States.PercentState)
async def configure_share(message: Message, state: FSMContext):
    
    if message.from_user is None:
        await message.answer("Пользователь не найден")
        return
    
    if message.text is None:
        await message.answer("Корректно отправьте Ваш процент(Например: 20)")
        return
            
    raw_text = message.text.strip('%,.!-+')
    
    try:
        percent = int(raw_text)
    except ValueError:
        await message.answer("Корректно отправьте Ваш процент(Например: 20)")
        return
    
    if not (0 <= percent <= 100):
        await message.answer("Процент должен быть в диапазоне от 0 до 100")
        return
    
    await change_share(message.from_user.id, percent)
    await message.answer(f"Процент изменен на {percent}")
    await state.clear()
    await start_message(message, state)