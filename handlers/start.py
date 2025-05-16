from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
import config
import database.requests
from database.db import async_session
from database.requests import set_user
from database.db import User

router = Router()
router.message.filter(F.chat.type == 'private')
API_TOKEN = config.TOKEN

bot = Bot(token=API_TOKEN)


# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username or "Unknown")

    text = (f'Добро пожаловать в <b>@oncologica_ru_bot</b>!\n'
            f'Пожалуйста, ознакомьтесь с публичной офертой и подтвердите свое согласие на обработку '
            f'Ваших персональных данных.')

    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == message.from_user.id))

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Ознакомиться',
                                  url='https://oncologica.ru/wp-content/uploads/2022/08/PUBLICHNAYA_OFERTA_O_ZAKLYUCHENII_DOGOVORA_POZHERTVOVANIYA.pdf')],
            [InlineKeyboardButton(text='Согласен(-на)', callback_data='start_agree')]
        ])

    await message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)


# Состояние ожидания телефона
class WaitPhoneFSM(StatesGroup):
    waiting_for_phone = State()


# Обработчик кнопки "Согласен(-на)"
@router.callback_query(F.data == 'start_agree')
async def start_agree(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    text = (f'Для старта оставьте, пожалуйста, свой <b>НОМЕР ТЕЛЕФОНА</b>.\nВоспользуйтесь кнопкой '
          f'<i>«Поделиться номером телефона»</i> '
          f'и получите чек-лист по профилактике онкозаболеваний <b>абсолютно бесплатно!</b>')

    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Поделиться номером телефона', request_contact=True),]
    ], resize_keyboard=True, one_time_keyboard=True)

    await callback.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
    await state.set_state(WaitPhoneFSM.waiting_for_phone)


# Обработчик телефона
@router.message(WaitPhoneFSM.waiting_for_phone)
async def get_number(message: Message, state: FSMContext):
    if message.contact:
        await database.requests.set_user_phone_and_name(tg_id=message.from_user.id,
                                                        user_name=message.contact.first_name,
                                                        phone_number=message.contact.phone_number)

        file_path = 'mediafiles/Чек-лист_ Профилактика онкологических заболеваний и чек-апы.pdf'
        input_file = FSInputFile(file_path)
        text = 'Спасибо! 🎉'
        # Отправка файла
        with open(file_path, 'rb') as file:
            await message.answer_document(text=text, document=input_file)

        # Отправка видео
        chat_id = message.chat.id
        await bot.send_video(chat_id, video=config.VIDEO_ID)

        green_block_text = ('🌸 Пожалуйста, выберите одну из предложенных сумм пожертвования или укажите свою. '
                            'Нажмите на кнопку «Другая сумма», чтобы ввести произвольную сумму.')
        green_block_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='1 480₽', callback_data='donate_1480'),
             InlineKeyboardButton(text='1 290₽', callback_data='donate_1290'),
             InlineKeyboardButton(text='990₽', callback_data='donate_990')],
            [InlineKeyboardButton(text='760₽', callback_data='donate_760'),
             InlineKeyboardButton(text='400₽', callback_data='donate_400'),
             InlineKeyboardButton(text='180₽', callback_data='donate_180')],
            [InlineKeyboardButton(text='Другая сумма', callback_data='donate_another_amount')]
        ])

        await message.answer(text=green_block_text, reply_markup=green_block_markup)

        await state.clear()
    else:
        text = 'Пожалуйста, нажмите на кнопку "Поделиться номером телефона", чтобы продолжить использовать бот.'

        await message.answer(text)
        return
