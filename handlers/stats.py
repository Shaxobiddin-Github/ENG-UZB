from aiogram.types import Message
from utils.stats_manager import get_user_stats

async def send_stats(message: Message):
    """Foydalanuvchi statistikasini ko‘rsatadi."""
    try:
        user_id = str(message.from_user.id)
        stats = get_user_stats(user_id)
        
        response = (
            f"📊 Statistika\n"
            f"🧪 Testlar: {stats['tests']}\n"
            f"📚 Ko‘rilgan darslar: {len(stats['completed_lessons'])}\n"
            f"🏆 Daraja: {stats['level']}\n"
            f"🎯 Umumiy ball: {stats['score']:.1f}"
        )
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}")