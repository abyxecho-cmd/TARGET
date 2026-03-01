import os
import discord
import asyncio
import requests
from datetime import datetime

# Environment variables
TOKEN = os.getenv('TOKEN')
# Virgülle ayrılmış ID'leri listeye çeviriyoruz
TARGET_IDS = [int(i.strip()) for i in os.getenv('TARGET_ID').split(',')]
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MySelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Her hedef için ayrı takip sözlüğü
        self.targets = {tid: {"last_time": datetime.now(), "notified": False} for tid in TARGET_IDS}

    async def on_ready(self):
        print(f'{self.user} aktif! Takip edilen kişi sayısı: {len(TARGET_IDS)}')
        self.loop.create_task(self.check_all_silence())

    async def on_message(self, message):
        # Eğer mesajı atan kişi takip listemizdeyse
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid]["last_time"] = datetime.now()
            # Eğer daha önce sessiz uyarısı verildiyse, tekrar aktif olduğunu loglayabiliriz
            if self.targets[uid]["notified"]:
                print(f"Hedef {uid} tekrar aktif oldu.")
            self.targets[uid]["notified"] = False

    async def check_all_silence(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now()
            for uid, data in self.targets.items():
                delta = (now - data["last_time"]).total_seconds()
                
                # Belirlenen süre dolduysa ve henüz bildirim gitmediyse
                if delta >= (BEKLEME_SURESI * 60) and not data["notified"]:
                    self.send_to_webhook(uid)
                    self.targets[uid]["notified"] = True
            
            await asyncio.sleep(30) # 30 saniyede bir genel kontrol

    def send_to_webhook(self, user_id):
        payload = {
            "content": f"🔔 **Sessizlik Alarmı!**\n<@{user_id}> (ID: {user_id}) tam {BEKLEME_SURESI} dakikadır mesaj göndermiyor.",
            "username": "Hedef Takip Sistemi"
        }
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Webhook hatası: {e}")

client = MySelfBot()
client.run(TOKEN)
