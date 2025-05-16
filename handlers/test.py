from aiogram.types import Message
import random
import json
import os

async def send_weekly_test(message: Message):
    try:
        json_path = os.path.join("data", "test_questions.json")
        if not os.path.exists(json_path):
            await message.answer("Xatolik: test_questions.json fayli topilmadi!")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question = random.choice(data)
        response = (
            f"🧪 *Weekly Test*\n"
            f"❓ *Question:* {question['question']}\n"
            f"1. {question['options'][0]}\n"
            f"2. {question['options'][1]}\n"
            f"3. {question['options'][2]}\n"
            f"4. {question['options'][3]}\n\n"
            f"Reply with the number (1-4)."
        )
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")