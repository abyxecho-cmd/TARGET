import os
import discord
import asyncio
import requests
from datetime import datetime

# Ortam Değişkenleri (Render Panelinden)
TOKEN = os.getenv('TOKEN')
TARGET_ID_STR = os.getenv('TARGET_ID', '')
TARGET_IDS = [int(i.strip()) for i in TARGET_ID_STR.split(',') if i.strip()]
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI', 5))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MySelfBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Her hedef için detaylı veri takibi
        self.targets = {}
        for tid in TARGET_IDS:
            self.targets[tid] = {
                "last_time": datetime.now(),
                "last_msg_content": "Mesaj bulunamadı.",
                "last_msg_url": "#",
                "notified": False
            }

    async def on_ready(self):
        print(f'--- Sistem Aktif ---')
        self.loop.create_task(self.check_all_silence())

    async def on_message(self, message):
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid].update({
                "last_time": datetime.now(),
                "last_msg_content": message.content if message.content else "[Görsel/Ek]",
                "last_msg_url": message.jump_url,
                "notified": False
            })

    async def check_all_silence(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now()
            for uid, data in self.targets.items():
                elapsed = (now - data["last_time"]).total_seconds()
                
                if elapsed >= (BEKLEME_SURESI * 60) and not data["notified"]:
                    self.send_styled_webhook(uid, data)
                    data["notified"] = True
            
            await asyncio.sleep(20)

    def send_styled_webhook(self, user_id, data):
        last_time_str = data["last_time"].strftime("%H:%M:%S")
        
        # Tam olarak istediğin metin formatı
        content = (
            f"<@{user_id}> @everyone\n"
            f"**KULANICI İT GİBİ SUSMUŞTUR XD**\n"
            f"**Kullanıcı ID:** `{user_id}`\n"
            f"**Süre:** {BEKLEME_SURESI} dakikadır mesaj yok.\n"
            f"**Son Mesaj Saati:** {last_time_str}\n"
            f"**Son Mesaj:** {data['last_msg_content']}\n"
            f"**Git:** [Mesaja Git]({data['last_msg_url']})"
        )

        payload = {
            "content": content,
            "username": "TARGET"
        }
        
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except Exception as e:
            print(f"Webhook hatası: {e}")

client = MySelfBot()
client.run(TOKEN)
