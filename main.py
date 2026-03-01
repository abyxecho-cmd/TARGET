import os
import discord
import asyncio
import requests
from datetime import datetime

# Environment variables
TOKEN = os.getenv('TOKEN')
TARGET_ID = int(os.getenv('TARGET_ID'))
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_message_time = datetime.now()
        self.is_silent = False

    async def setup_hook(self):
        # Arka plan görevini başlat
        self.loop.create_task(self.monitor_silence())

    def send_webhook(self):
        data = {
            "content": f"⚠️ **Hedef Sessiz!**\n<@{TARGET_ID}> tam {BEKLEME_SURESI} dakikadır mesaj atmıyor.",
            "username": "Sessizlik Dedektörü"
        }
        requests.post(WEBHOOK_URL, json=data)

    async def monitor_silence(self):
        await self.wait_until_ready()
        while not self.is_closed():
            elapsed = (datetime.now() - self.last_message_time).total_seconds()
            if elapsed >= (BEKLEME_SURESI * 60) and not self.is_silent:
                self.send_webhook()
                self.is_silent = True
            await asyncio.sleep(20) # 20 saniyede bir kontrol

    async def on_message(self, message):
        if message.author.id == TARGET_ID:
            self.last_message_time = datetime.now()
            self.is_silent = False

# Intents ayarları (Önemli: Developer Portal'dan hepsini açın)
intents = discord.Intents.all()
client = MyBot(intents=intents)

client.run(TOKEN)
