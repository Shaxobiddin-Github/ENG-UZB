from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import Command, StateFilter
import logging
import asyncio
from handlers.vocabulary import send_word, start_test, process_test_answer, TestState
from handlers.grammar import send_grammar
from handlers.listening import send_listening
from handlers.speaking import send_speaking_prompt
from handlers.test import send_weekly_test
from handlers.stats import send_stats
from handlers.lessons import start_lesson, start_test_selection, process_lesson, process_test, process_lesson_test_answer, show_rating, start_game, process_game_answer, start_pronounce, process_pronounce_answer, stop_pronounce, process_language_selection, back_to_language, LessonState, GameState, PronounceState

# Bot tokeningiz
API_TOKEN = '7775904021:AAHcsTAzr9eS-VNL3DWKlGUYI9_0KxYLbwc'

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlarini yaratamiz
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Menyu buyruqlarini sozlash
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Boshlash"),
        BotCommand(command="soz", description="SO‘Z"),
        BotCommand(command="test", description="TEST"),
        BotCommand(command="rating", description="REYTING"),
        BotCommand(command="grammatika", description="GRAMMATIKA"),
        BotCommand(command="tinglash", description="TINGLASH"),
        BotCommand(command="gapirish", description="GAPIRISH"),
        BotCommand(command="statistika", description="STATISTIKA"),
        BotCommand(command="lesson", description="DARS"),
        BotCommand(command="play", description="O'YIN"),
        BotCommand(command="pronounce", description="TALAFFUZ")
    ]
    try:
        await bot.set_my_commands(commands)
        logging.info("Menyu buyruqlari muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logging.error(f"Menyu buyruqlarini o'rnatishda xatolik: {e}")

# /start buyrug'i uchun handler
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("📚 *Ingliz tili botiga xush kelibsiz!*\nQuyidagi bo‘limlardan birini tanlash uchun menyuni oching yoki /lesson bilan dars boshlang:", parse_mode='Markdown')

# Darslar, testlar, o'yin va talaffuz uchun handlerlar
dp.message.register(start_lesson, Command('lesson'))
dp.message.register(start_test_selection, Command('test'))
dp.callback_query.register(process_lesson, lambda c: c.data.startswith("lesson_"))
dp.callback_query.register(process_test, lambda c: c.data.startswith("test_"))
dp.message.register(process_lesson_test_answer, StateFilter(TestState.waiting_for_answer))
dp.message.register(show_rating, Command('rating'))
dp.message.register(start_game, Command('play'))
dp.message.register(process_game_answer, StateFilter(GameState.waiting_for_answer))  # waiting_for_guess → waiting_for_answer
dp.message.register(start_pronounce, Command('pronounce'))
dp.message.register(process_pronounce_answer, StateFilter(PronounceState.waiting_for_word))
dp.callback_query.register(process_language_selection, lambda c: c.data.startswith("lang_"))
dp.callback_query.register(back_to_language, lambda c: c.data == "back_to_lang")
dp.callback_query.register(stop_pronounce, lambda c: c.data == "stop")

# Boshqa handlerlarni ro'yxatdan o'tkazamiz
dp.message.register(send_word, Command('soz'))
dp.message.register(start_test, Command('test'))
dp.message.register(process_test_answer, StateFilter(TestState.waiting_for_answer))
dp.message.register(send_grammar, Command('grammatika'))
dp.message.register(send_listening, Command('tinglash'))
dp.message.register(send_speaking_prompt, Command('gapirish'))
dp.message.register(send_weekly_test, Command('weekly_test'))
dp.message.register(send_stats, Command('statistika'))

# Botni ishga tushirish
async def main():
    try:
        await set_bot_commands()
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())