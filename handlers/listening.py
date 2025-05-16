from aiogram.types import Message

async def send_listening(message: Message):
    try:
        response = "🎧 *Tinglash mashqlari uchun audio yuklab oling yoki quyidagi havolalardan foydalaning:*\n- /audio1 - Boshlang‘ich daraja\n- /audio2 - O‘rta daraja"
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")