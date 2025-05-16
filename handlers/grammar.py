from aiogram.types import Message

async def send_grammar(message: Message):
    try:
        response = "📚 *Grammatika mashqlari uchun quyidagi buyruqlardan foydalaning:*\n- /noun - Otlar\n- /verb - Fe’llar\n- /sentence - Jumlalar"
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")