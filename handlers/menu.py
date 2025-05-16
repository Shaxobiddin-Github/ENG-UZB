from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

async def show_menu(message: Message):
    # Inline keyboard yaratamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="SO‘Z", callback_data="soz")],
        [InlineKeyboardButton(text="TEST", callback_data="test")],
        [InlineKeyboardButton(text="GRAMMATIKA", callback_data="grammatika")],
        [InlineKeyboardButton(text="TINGLASH", callback_data="tinglash")],
        [InlineKeyboardButton(text="GAPIRISH", callback_data="gapirish")],
        [InlineKeyboardButton(text="STATISTIKA", callback_data="statistika")]
    ])

    await message.answer("📚 *Ingliz tili botiga xush kelibsiz!*\nQuyidagi bo‘limlardan birini tanlang:", reply_markup=keyboard, parse_mode='Markdown')