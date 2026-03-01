import os
import discord
import asyncio
import requests
from datetime import datetime

# Ortam Değişkenleri
TOKEN = os.getenv('TOKEN')
TARGET_ID_STR = os.getenv('TARGET_ID', '')
TARGET_IDS = [int(i.strip()) for i in TARGET_ID_STR.split(',') if i.strip()]
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI', 1))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MySelfBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.targets = {}
        for tid in TARGET_IDS:
            self.targets[tid] = {
                "last_time": datetime.now(),
                "last_msg_content": "Sistem başladıktan sonra henüz mesaj atmadı.",
                "last_msg_url": "https://discord.com", # Boş link yerine ana link
                "notified": False
            }

    async def on_ready(self):
        print(f'--- Takip Sistemi Aktif ---')
        self.loop.create_task(self.check_silence_loop())

    async def on_message(self, message):
        # Mesaj geldiği an linki ve içeriği hafızaya alıyoruz
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid].update({
                "last_time": datetime.now(),
                "last_msg_content": message.content if message.content else "[Görsel/Ek]",
                "last_msg_url": message.jump_url, # Link burada oluşturulur
                "notified": False 
            })

    async def check_silence_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now()
            for uid, data in self.targets.items():
                elapsed = (now - data["last_time"]).total_seconds()
                
                if elapsed >= (BEKLEME_SURESI * 60) and not data["notified"]:
                    self.send_target_webhook(uid, data)
                    data["notified"] = True
            
            await asyncio.sleep(15)

    def send_target_webhook(self, user_id, data):
        last_time_str = data["last_time"].strftime("%H:%M:%S")
        
        # Linkin çalışması için markdown formatı (Link Mavi Olur)
        content = (
            f"<@{user_id}> @everyone\n"
            f"**KULANICI İT GİBİ SUSMUŞTUR XD**\n"
            f"**Kullanıcı ID:** `{user_id}`\n"
            f"**Süre:** {BEKLEME_SURESI} dakikadır mesaj yok.\n"
            f"**Son Mesaj Saati:** {last_time_str}\n"
            f"**Son Mesaj:** {data['last_msg_content']}\n"
            f"**Git:** [Mesaja Git]({data['last_msg_url']})"
        )

        payload = {"content": content, "username": "Shattered Sun Target Sistemi"}
        requests.post(WEBHOOK_URL, json=payload)

client = MySelfBot()
client.run(TOKEN)
