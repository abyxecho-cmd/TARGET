import os
import discord
import asyncio
import requests
from datetime import datetime

# Environment variables
TOKEN = os.getenv('TOKEN')
TARGET_ID_STR = os.getenv('TARGET_ID', '')
TARGET_IDS = [int(i.strip()) for i in TARGET_ID_STR.split(',') if i.strip()]
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI', 1))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MySelfBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Her hedef için takip verisi
        self.targets = {tid: {"last_time": datetime.now(), "notified": False} for tid in TARGET_IDS}

    async def on_ready(self):
        print(f'Giriş yapıldı: {self.user}')
        print(f'Takip edilen ID listesi: {TARGET_IDS}')
        self.loop.create_task(self.check_all_silence())

    async def on_message(self, message):
        # Mesajı atan kişi listedeyse süreyi sıfırla
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid]["last_time"] = datetime.now()
            self.targets[uid]["notified"] = False

    async def check_all_silence(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now()
            for uid, data in self.targets.items():
                elapsed = (now - data["last_time"]).total_seconds()
                
                # Süre dolduysa ve henüz bildirim gitmediyse
                if elapsed >= (BEKLEME_SURESI * 60) and not data["notified"]:
                    self.send_to_webhook(uid)
                    data["notified"] = True
            
            await asyncio.sleep(20) # 20 saniyede bir kontrol et

    def send_to_webhook(self, user_id):
        payload = {
            "content": f"🔔 **Sessizlik Bildirimi**\n<@{user_id}> (ID: {user_id}) kullanıcısı {BEKLEME_SURESI} dakikadır mesaj atmıyor.",
            "username": "Hedef Takip"
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Webhook hatası: {e}")

# Self-bot kütüphanesinde Intents bazen sorun çıkarabilir, 
# bu yüzden en temel haliyle başlatıyoruz.
client = MySelfBot()
client.run(TOKEN)
