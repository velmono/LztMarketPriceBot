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


router = Router()
router.message.filter(F.chat.type.in_([ChatType.PRIVATE]))


class States(StatesGroup):
    StartState = State()
    CheckState = State()


@router.message(Command("start", prefix="/!"))
async def start_message(message: Message, state: FSMContext):
    links_button = KeyboardButton(text="Проверить ссылки")
    
    keyboard = ReplyKeyboardMarkup(keyboard=[[links_button]],resize_keyboard=True)
    
    await message.answer(text="Привет\nНажми: Проверить ссылки",
                     reply_markup=keyboard
                     )


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_operation(message: Message, state: FSMContext):
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer("Отменено")


@router.message(F.text == "Проверить ссылки")
async def answer_links(message: Message, state: FSMContext):
    await state.set_state(States.CheckState)
    await message.answer("Отправь ссылки/ID\n(Каждая ссылка/каждый ID с новой строки)")


@router.message(States.CheckState)
async def check_links(message: Message, state: FSMContext):
    if message.text is not None:
        links = message.text.split()
        await message.answer(f"Готово ваш отчет:\n{await create_report(links)}")
        await state.clear()
    else:
        await message.answer("Отправьте ссылки корректно")
        await state.set_state(States.CheckState)
    
