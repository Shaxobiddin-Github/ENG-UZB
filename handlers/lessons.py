from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
import os
import random
from gtts import gTTS
from googletrans import Translator
from eng_to_ipa import convert
from handlers.vocabulary import TestState
from themes import LESSONS

class LessonState(StatesGroup):
    waiting_for_lesson = State()

class GameState(StatesGroup):
    waiting_for_answer = State()  # Javob kutilishi uchun
    game_data = State()          # O‘yin ma’lumotlari uchun

class PronounceState(StatesGroup):
    waiting_for_language = State()
    waiting_for_word = State()












# JSON fayl bilan ishlash uchun funksiyalar
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# So'zning bir qismini yashirish uchun funksiya
def create_hint(word):
    if len(word) < 3:
        return word
    indices = random.sample(range(len(word)), len(word) // 2)
    hint = list(word)
    for i in indices:
        hint[i] = "_"
    return "".join(hint)

# Talaffuzni generatsiya qilish
def synthesize_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "output.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        return None

# Maxsus lug'at: o'zbekcha so'zlar uchun inglizcha tarjima
UZ_TO_EN_DICT = {
    "salom": "hello",
    "rahmat": "thank you",
    "yaxshi": "good",
    "qalay": "how",
    "kitob": "book"
}

# Maxsus lug'at: inglizcha so'zlar uchun o'zbekcha tarjima
EN_TO_UZ_DICT = {
    "hello": "salom",
    "thank you": "rahmat",
    "good": "yaxshi",
    "how": "qalay",
    "book": "kitob"
}

# Barcha so‘zlarni yig‘ish
def get_all_words():
    all_words = []
    for lesson in LESSONS.values():
        all_words.extend(lesson["words"])
    return all_words

async def start_lesson(message: Message, state: FSMContext):
    try:
        await state.set_state(LessonState.waiting_for_lesson)
        lessons = list(LESSONS.keys())
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=lesson.upper(), callback_data=f"lesson_{lesson}") for lesson in lessons[i:i+2]]
            for i in range(0, len(lessons), 2)
        ])
        await message.answer("Darsni tanlang:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def start_test_selection(message: Message, state: FSMContext):
    try:
        lessons = list(LESSONS.keys())
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=lesson.upper(), callback_data=f"test_{lesson}") for lesson in lessons[i:i+2]]
            for i in range(0, len(lessons), 2)
        ])
        await message.answer("Test uchun mavzuni tanlang:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_lesson(callback_query: CallbackQuery, state: FSMContext):
    try:
        lesson_id = callback_query.data.replace("lesson_", "")
        lesson = LESSONS.get(lesson_id)
        if not lesson:
            await callback_query.answer("Dars topilmadi!")
            return

        description = lesson["description"]
        video_url = lesson["video_url"]
        examples = "\n".join([f"- {ex}" for ex in lesson["examples"]])
        words = "\n".join([f"- {w['word']} - {w['translation']}" for w in lesson["words"]])

        response_part1 = (
            f"{lesson['title']}\n"
            f"{description}\n\n"
            f"Video: {video_url}\n\n"
            f"Misollar:\n{examples}"
        )
        await callback_query.message.answer(response_part1)

        await callback_query.message.answer(
            f"Yodlash uchun 30 ta so‘z (keyingi darsgacha yodlang):\n{words}\n\n"
            f"Vazifa: Ushbu so‘zlarni yodlab oling va keyingi darsda testdan o‘tasiz."
        )

        test_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Testni boshlash", callback_data=f"test_{lesson_id}")]
        ])
        await callback_query.message.answer("Dars tugadi! Testni boshlamoqchimisiz?", reply_markup=test_keyboard)

        await state.update_data(lesson_id=lesson_id, words=lesson["words"])
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_test(callback_query: CallbackQuery, state: FSMContext):
    try:
        lesson_id = callback_query.data.replace("test_", "")
        lesson = LESSONS.get(lesson_id)
        if not lesson:
            await callback_query.answer("Mavzu topilmadi!")
            return

        words = lesson["words"]
        if not words:
            await callback_query.answer("So‘zlar topilmadi!")
            return

        questions = []
        for word in words:
            options = [word["translation"]]
            all_translations = [w["translation"] for w in words if w["translation"] != word["translation"]]
            wrong_options = random.sample(all_translations, min(3, len(all_translations))) if all_translations else []
            options.extend(wrong_options)
            while len(options) < 4:
                options.append(random.choice(all_translations))
            random.shuffle(options)
            correct_answer = options.index(word["translation"]) + 1
            questions.append({
                "word": word["word"],
                "options": options,
                "correct_answer": correct_answer
            })

        await state.update_data(questions=questions, current_question=0, correct_answers=0)
        question = questions[0]
        response = (
            f"❓ Test 1/30: `{question['word']}` so‘zining to‘g‘ri tarjimasi qaysi?\n\n"
            f"1. {question['options'][0]}\n"
            f"2. {question['options'][1]}\n"
            f"3. {question['options'][2]}\n"
            f"4. {question['options'][3]}\n\n"
            f"Javobingizni raqam sifatida yuboring (1-4)."
        )
        await callback_query.message.answer(response, parse_mode='Markdown')
        await state.set_state(TestState.waiting_for_answer)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_lesson_test_answer(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        user_answer = message.text.strip()
        if not user_answer.isdigit() or int(user_answer) not in range(1, 5):
            await message.answer("Iltimos, 1 dan 4 gacha bo'lgan raqam yuboring.")
            return

        user_answer = int(user_answer)
        data = await state.get_data()
        questions = data.get('questions', [])
        current_question = data.get('current_question', 0)
        correct_answers = data.get('correct_answers', 0)

        question = questions[current_question]
        correct_answer = question['correct_answer']

        if user_answer == correct_answer:
            correct_answers += 1
            await message.answer("✅ To‘g‘ri javob! 🎉")
        else:
            await message.answer(f"❌ Noto‘g‘ri javob. To‘g‘ri javob: {correct_answer}.")

        current_question += 1
        if current_question < len(questions):
            question = questions[current_question]
            response = (
                f"❓ Test {current_question + 1}/30: `{question['word']}` so‘zining to‘g‘ri tarjimasi qaysi?\n\n"
                f"1. {question['options'][0]}\n"
                f"2. {question['options'][1]}\n"
                f"3. {question['options'][2]}\n"
                f"4. {question['options'][3]}\n\n"
                f"Javobingizni raqam sifatida yuboring (1-4)."
            )
            await message.answer(response, parse_mode='Markdown')
            await state.update_data(current_question=current_question, correct_answers=correct_answers)
        else:
            percentage = (correct_answers / 30) * 100
            users = load_users()
            if str(user_id) not in users:
                users[str(user_id)] = {"score": 0, "tests": 0}
            users[str(user_id)]["score"] += correct_answers * 10
            users[str(user_id)]["tests"] += 1
            save_users(users)

            response = (
                f"🏁 Test yakunlandi!\n"
                f"✅ To‘g‘ri javoblar: {correct_answers}/30\n"
                f"📊 Foiz: {percentage:.2f}%\n"
                f"🎉 Umumiy ballingiz: {users[str(user_id)]['score']}\n"
                f"Natijangiz: {'Ajoyib!' if percentage >= 80 else 'Yaxshi!' if percentage >= 60 else 'Yana harakat qiling!'}"
            )
            await message.answer(response, parse_mode='Markdown')
            await state.clear()
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def show_rating(message: Message):
    try:
        users = load_users()
        username = message.from_user.username
        if not users:
            await message.answer("Hozircha reyting ma'lumotlari yo'q.")
            return

        sorted_users = sorted(users.items(), key=lambda x: x[1]["score"], reverse=True)
        response = "🏆 Reyting:\n"
        for i, (user_id, data) in enumerate(sorted_users, 1):
            response += f"{i}. Foydalanuvchi {username} - {data['score']} ball, {data['tests']} ta test\n"
        await message.answer(response)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def start_game(message: Message, state: FSMContext):
    try:
        all_words = get_all_words()
        if not all_words:
            await message.answer("So‘zlar topilmadi!")
            return

        current_words = random.sample(all_words, 10)  # 10 ta tasodifiy so‘z
        current_index = 0
        word = current_words[current_index]["word"]
        audio_file = synthesize_speech(word)
        if audio_file:
            audio = FSInputFile(audio_file)
            await message.answer_audio(audio, caption=f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring.")
            os.remove(audio_file)
        else:
            await message.answer(f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring (audio yuklanmadi).")

        await state.set_state(GameState.waiting_for_answer)
        await state.update_data(
            words=current_words,
            current_index=current_index,
            attempts=3,
            total_score=0.0
        )
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_game_answer(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        user_answer = message.text.strip().lower()
        data = await state.get_data()
        words = data.get("words", [])
        current_index = data.get("current_index", 0)
        attempts = data.get("attempts", 3)
        total_score = data.get("total_score", 0.0)

        if current_index >= len(words):
            users = load_users()
            if str(user_id) not in users:
                users[str(user_id)] = {"score": 0, "tests": 0}
            users[str(user_id)]["score"] += total_score
            users[str(user_id)]["tests"] += 1
            save_users(users)
            await message.answer(f"🏁 O‘yin tugadi!\nUmumiy ballingiz: {total_score:.1f}\nUmumiy hisobingiz: {users[str(user_id)]['score']}")
            await state.clear()
            return

        correct_word = words[current_index]["word"].lower()
        if user_answer == correct_word:
            score = 1.3 if attempts == 3 else 1.2 if attempts == 2 else 1.0
            total_score += score
            await message.answer(f"✅ To‘g‘ri javob! +{score} ball qo‘shildi.\nJami ball: {total_score:.1f}")
            current_index += 1
            if current_index < len(words):
                word = words[current_index]["word"]
                audio_file = synthesize_speech(word)
                if audio_file:
                    audio = FSInputFile(audio_file)
                    await message.answer_audio(audio, caption=f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring.")
                    os.remove(audio_file)
                else:
                    await message.answer(f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring (audio yuklanmadi).")
                await state.update_data(current_index=current_index, attempts=3, total_score=total_score)
            else:
                users = load_users()
                if str(user_id) not in users:
                    users[str(user_id)] = {"score": 0, "tests": 0}
                users[str(user_id)]["score"] += total_score
                users[str(user_id)]["tests"] += 1
                save_users(users)
                await message.answer(f"🏁 O‘yin tugadi!\nUmumiy ballingiz: {total_score:.1f}\nUmumiy hisobingiz: {users[str(user_id)]['score']}")
                await state.clear()
        else:
            attempts -= 1
            if attempts > 0:
                await message.answer(f"❌ Noto‘g‘ri javob. Qoldi: {attempts} urinish.\nYana urinib ko‘ring!")
                await state.update_data(attempts=attempts)
            else:
                total_score -= 0.5
                await message.answer(f"❌ Urinishlar tugadi! To‘g‘ri javob: {correct_word}\n-0.5 ball ayirildi.\nJami ball: {total_score:.1f}")
                current_index += 1
                if current_index < len(words):
                    word = words[current_index]["word"]
                    audio_file = synthesize_speech(word)
                    if audio_file:
                        audio = FSInputFile(audio_file)
                        await message.answer_audio(audio, caption=f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring.")
                        os.remove(audio_file)
                    else:
                        await message.answer(f"🎮 So‘zni toping! {current_index + 1}/10\nUrinishlaringiz: 3\nJavobni yuboring (audio yuklanmadi).")
                    await state.update_data(current_index=current_index, attempts=3, total_score=total_score)
                else:
                    users = load_users()
                    if str(user_id) not in users:
                        users[str(user_id)] = {"score": 0, "tests": 0}
                    users[str(user_id)]["score"] += total_score
                    users[str(user_id)]["tests"] += 1
                    save_users(users)
                    await message.answer(f"🏁 O‘yin tugadi!\nUmumiy ballingiz: {total_score:.1f}\nUmumiy hisobingiz: {users[str(user_id)]['score']}")
                    await state.clear()
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def start_pronounce(message: Message, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="Inglizcha", callback_data="lang_en")],
            [InlineKeyboardButton(text="Stop", callback_data="stop")]
        ])
        await state.set_state(PronounceState.waiting_for_language)
        await message.answer("Iltimos, tilni tanlang:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_language_selection(callback_query: CallbackQuery, state: FSMContext):
    try:
        lang = callback_query.data.replace("lang_", "")
        await state.update_data(selected_lang=lang)
        await state.set_state(PronounceState.waiting_for_word)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Stop", callback_data="stop")]
        ])
        await callback_query.message.edit_text("Marhamat, so‘z kiriting. Jarayonni to‘xtatish uchun 'Stop' tugmasini bosing.", reply_markup=keyboard)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_pronounce_answer(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        selected_lang = data.get("selected_lang", "en")
        word = message.text.strip().lower()

        if selected_lang == "uz":
            translated = UZ_TO_EN_DICT.get(word, "N/A")
            if translated == "N/A":
                translator = Translator()
                translated = translator.translate(word, src='uz', dest='en').text.lower()
            ipa = convert(translated) if translated != "N/A" else "N/A"
            audio_file = synthesize_speech(translated) if translated != "N/A" else None
            if audio_file:
                audio = FSInputFile(audio_file)
                await message.answer_audio(audio, caption=f"🔊 So‘z: {word}\nTalaffuz (IPA): {ipa}\nInglizcha tarjima: {translated}")
                os.remove(audio_file)
            else:
                await message.answer(f"🔊 So‘z: {word}\nTalaffuz (IPA): {ipa}\nInglizcha tarjima: {translated}\nAudio generatsiya qila olmadim.")
        else:
            translated = EN_TO_UZ_DICT.get(word, "N/A")
            if translated == "N/A":
                translator = Translator()
                translated = translator.translate(word, src='en', dest='uz').text.lower()
            ipa = convert(word)
            audio_file = synthesize_speech(word)
            if audio_file:
                audio = FSInputFile(audio_file)
                await message.answer_audio(audio, caption=f"🔊 So‘z: {word}\nTalaffuz (IPA): {ipa}\nO‘zbekcha tarjima: {translated}")
                os.remove(audio_file)
            else:
                await message.answer(f"🔊 So‘z: {word}\nTalaffuz (IPA): {ipa}\nO‘zbekcha tarjima: {translated}\nAudio generatsiya qila olmadim.")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ortga", callback_data="back_to_lang")],
            [InlineKeyboardButton(text="Stop", callback_data="stop")]
        ])
        await message.answer("Yana so‘z kiritishingiz mumkin yoki tugmalardan birini bosing.", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def back_to_language(callback_query: CallbackQuery, state: FSMContext):
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="Inglizcha", callback_data="lang_en")],
            [InlineKeyboardButton(text="Stop", callback_data="stop")]
        ])
        await state.set_state(PronounceState.waiting_for_language)
        await callback_query.message.edit_text("Iltimos, tilni tanlang:", reply_markup=keyboard)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Xatolik yuz berdi: {str(e)}")

async def stop_pronounce(callback_query: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await state.set_state(None)
        bot_info = (
            "📚 *Ingliz Tili O‘quv Boti*\n\n"
            "Bu bot sizga ingliz tilini o‘rganishda yordam beradi! Quyidagi funksiyalarni sinab ko‘ring:\n\n"
            "🔹 *Buyruqlar Ro‘yxati:*\n"
            "- /start - Botni boshlash\n"
            "- /soz - Yangi so‘z o‘rganish\n"
            "- /test - So‘zlar bo‘yicha test\n"
            "- /rating - Reytingni ko‘rish\n"
            "- /grammatika - Grammatika darsi\n"
            "- /tinglash - Tinglash mashqlari\n"
            "- /gapirish - Gapirish mashqlari\n"
            "- /statistika - O‘quv statistikangiz\n"
            "- /lesson - Darslar\n"
            "- /play - So‘z topish o‘yini\n"
            "- /pronounce - Talaffuz mashqlari\n\n"
            "🔹 *Foydalanish Qo‘llanmasi:*\n"
            "1. /start buyrug‘i bilan boshlang.\n"
            "2. O‘zingizga kerakli bo‘limni tanlang.\n"
            "3. Har bir bo‘limda ko‘rsatmalarga rioya qiling.\n"
            "4. Talaffuz mashqlarida tilni tanlab, so‘z kiritishingiz mumkin.\n\n"
            "📅 *Bugungi Sana:* 15-may, 2025-yil\n"
            "📩 Yangi funksiyalar uchun takliflaringizni yuboring!"
        )
        await callback_query.message.edit_text(bot_info, parse_mode='Markdown', reply_markup=None)
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"Xatolik yuz berdi: {str(e)}")