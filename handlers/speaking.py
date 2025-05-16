from aiogram.types import Message

async def send_speaking_prompt(message: Message):
    try:
        response = "🗣️ *Gapirish mashqlari uchun prompt:*\nPrompt: Tell me about your favorite hobby."
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")