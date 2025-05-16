from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import json
import os
from utils.stats_manager import update_word_stat, update_test_stat

class TestState(StatesGroup):
    waiting_for_answer = State()

async def send_word(message: Message):
    try:
        json_path = os.path.join("data", "vocabulary.json")
        if not os.path.exists(json_path):
            await message.answer("Xatolik: vocabulary.json fayli topilmadi!")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_topics = list(data.keys())
        topic = random.choice(all_topics)
        word_data = random.choice(data[topic])

        response = (
            f"📚 *Word:* `{word_data['word']}`\n"
            f"🇺🇿 *Translation:* {word_data['translation']}\n"
            f"💬 *Example:* _{word_data['example']}_\n"
            f"🔖 *Topic:* `{topic}`"
        )
        await message.answer(response, parse_mode='Markdown')

        # Statistikani yangilash
        try:
            user_id = str(message.from_user.id)
            update_word_stat(user_id)
        except Exception as e:
            print(f"Statistikani yangilashda xatolik: {e}")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def start_test(message: Message, state: FSMContext):
    try:
        json_path = os.path.join("data", "vocabulary.json")
        if not os.path.exists(json_path):
            await message.answer("Xatolik: vocabulary.json fayli topilmadi!")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Barcha so'zlarni yig'ish
        all_words = []
        for topic in data:
            all_words.extend(data[topic])

        # 30 ta tasodifiy so'z tanlash
        if len(all_words) < 30:
            selected_words = all_words * (30 // len(all_words) + 1)
        selected_words = random.sample(all_words, 30)

        # Test savollarini tayyorlash
        questions = []
        for word in selected_words:
            all_translations = [item['translation'] for item in all_words if item['translation'] != word['translation']]
            wrong_words = random.sample(all_translations, 3) if len(all_translations) >= 3 else all_translations
            options = [word['translation']] + wrong_words
            random.shuffle(options)
            correct_answer_index = options.index(word['translation']) + 1
            questions.append({
                'word': word['word'],
                'options': options,
                'correct_answer': correct_answer_index
            })

        # Testni boshlash
        await state.set_state(TestState.waiting_for_answer)
        await state.update_data(questions=questions, current_question=0, correct_answers=0)

        # Birinchi savolni yuborish
        question = questions[0]
        response = (
            f"❓ *Test 1/30:* `{question['word']}` so‘zining to‘g‘ri tarjimasi qaysi?\n\n"
            f"1. {question['options'][0]}\n"
            f"2. {question['options'][1]}\n"
            f"3. {question['options'][2]}\n"
            f"4. {question['options'][3]}\n\n"
            f"Javobingizni raqam sifatida yuboring (1-4)."
        )
        await message.answer(response, parse_mode='Markdown')

        # Statistikani yangilash
        try:
            user_id = str(message.from_user.id)
            update_test_stat(user_id)
        except Exception as e:
            print(f"Test statistikasini yangilashda xatolik: {e}")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")

async def process_test_answer(message: Message, state: FSMContext):
    try:
        user_answer = message.text.strip()
        if not user_answer.isdigit() or int(user_answer) not in range(1, 5):
            await message.answer("Iltimos, 1 dan 4 gacha bo'lgan raqam yuboring.")
            return

        user_answer = int(user_answer)
        data = await state.get_data()
        questions = data.get('questions', [])
        current_question = data.get('current_question', 0)
        correct_answers = data.get('correct_answers', 0)

        # Joriy savolni tekshirish
        question = questions[current_question]
        correct_answer = question['correct_answer']

        if user_answer == correct_answer:
            correct_answers += 1
            await message.answer("✅ To‘g‘ri javob! 🎉")
        else:
            await message.answer(f"❌ Noto‘g‘ri javob. To‘g‘ri javob: {correct_answer}.")

        # Keyingi savolga o'tish
        current_question += 1
        if current_question < len(questions):
            # Keyingi savolni yuborish
            question = questions[current_question]
            response = (
                f"❓ *Test {current_question + 1}/30:* `{question['word']}` so‘zining to‘g‘ri tarjimasi qaysi?\n\n"
                f"1. {question['options'][0]}\n"
                f"2. {question['options'][1]}\n"
                f"3. {question['options'][2]}\n"
                f"4. {question['options'][3]}\n\n"
                f"Javobingizni raqam sifatida yuboring (1-4)."
            )
            await message.answer(response, parse_mode='Markdown')
            await state.update_data(current_question=current_question, correct_answers=correct_answers)
        else:
            # Test tugadi
            percentage = (correct_answers / 30) * 100
            response = (
                f"🏁 *Test yakunlandi!*\n"
                f"✅ To‘g‘ri javoblar: {correct_answers}/30\n"
                f"📊 Foiz: {percentage:.2f}%\n"
                f"🎉 Natijangiz: {'Ajoyib!' if percentage >= 80 else 'Yaxshi!' if percentage >= 60 else 'Yana harakat qiling!'}"
            )
            await message.answer(response, parse_mode='Markdown')
            await state.clear()

    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")