import os
import discord
import asyncio
import requests
from datetime import datetime
import pytz

# Ortam Değişkenleri
TOKEN = os.getenv('TOKEN')
TARGET_ID_STR = os.getenv('TARGET_ID', '')
TARGET_IDS = [int(i.strip()) for i in TARGET_ID_STR.split(',') if i.strip()]
MY_ID = os.getenv('MY_ID') # Seni etiketlemek için Render'dan girilmeli
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI', 1))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

TR_SAAT = pytz.timezone('Europe/Istanbul')

class MySelfBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.targets = {}
        for tid in TARGET_IDS:
            self.targets[tid] = {
                "last_time": None, 
                "last_msg_content": "Mesaj bekleniyor...",
                "last_msg_url": "https://discord.com",
                "notified": True 
            }

    async def on_ready(self):
        print(f'--- {self.user} Aktif | Saniye Takibi Başladı ---')
        self.loop.create_task(self.check_silence_loop())

    async def on_message(self, message):
        # Her saniye tüm mesajları izler
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid].update({
                "last_time": datetime.now(TR_SAAT),
                "last_msg_content": message.content if message.content else "[Ek/Görsel]",
                "last_msg_url": message.jump_url,
                "notified": False 
            })

    async def check_silence_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now(TR_SAAT)
            for uid, data in self.targets.items():
                if data["last_time"] is None or data["notified"]:
                    continue
                
                # Saniye saniye farkı hesapla
                diff = (now - data["last_time"]).total_seconds()
                
                if diff >= (BEKLEME_SURESI * 60):
                    self.send_styled_webhook(uid, data)
                    data["notified"] = True
            
            await asyncio.sleep(1) # Saniye hassasiyeti

    def send_styled_webhook(self, user_id, data):
        last_time_str = data["last_time"].strftime("%H:%M:%S")
        
        # Sadece seni etiketleyen ve istediğin formatta mesaj
        content = (
            f"<@{MY_ID}>\n"
            f"**KULANICI İT GİBİ SUSMUŞTUR XD**\n"
            f"**Kullanıcı ID:** `{user_id}`\n"
            f"**Süre:** {BEKLEME_SURESI} dakikadır mesaj yok.\n"
            f"**Son Mesaj Saati:** {last_time_str}\n"
            f"**Son Mesaj:** {data['last_msg_content']}\n"
            f"**Git:** [Mesaja Git]({data['last_msg_url']})"
        )

        payload = {"content": content, "username": "TARGET"}
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except:
            pass

client = MySelfBot()
client.run(TOKEN)
