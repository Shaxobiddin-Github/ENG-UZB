import asyncio
from aiogram import Bot
from datetime import datetime, time

async def schedule_reminders(bot: Bot):
    while True:
        now = datetime.now().time()
        if now.hour == 9 and now.minute == 0:  # Soat 9:00 da
            await bot.send_message(
                chat_id="YOUR_CHAT_ID",  # TODO: Foydalanuvchi IDlarini saqlash
                text="🌞 Good morning! Ready for today's English tasks? Try /word, /grammar, or /listening!"
            )
        await asyncio.sleep(60)  # Har daqiqada tekshirish