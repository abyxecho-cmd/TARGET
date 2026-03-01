import os
import discord
import asyncio
import requests
from datetime import datetime

# Ortam Değişkenleri (Render üzerinden okunur)
TOKEN = os.getenv('TOKEN')
TARGET_ID_STR = os.getenv('TARGET_ID', '')
TARGET_IDS = [int(i.strip()) for i in TARGET_ID_STR.split(',') if i.strip()]
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI', 1)) # Burada 1 yazıyorsa 1 dk sonra atar
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

class MySelfBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.targets = {}
        for tid in TARGET_IDS:
            self.targets[tid] = {
                "last_time": datetime.now(),
                "last_msg_content": "Mesaj bulunamadı.",
                "last_msg_url": "#",
                "notified": False
            }

    async def on_ready(self):
        print(f'--- Takip Sistemi Aktif ---')
        self.loop.create_task(self.check_silence_loop())

    async def on_message(self, message):
        # Eğer mesajı atan takip ettiğimiz kişiyse bilgileri tazele
        if message.author.id in self.targets:
            uid = message.author.id
            self.targets[uid].update({
                "last_time": datetime.now(),
                "last_msg_content": message.content if message.content else "[Ek/Görsel]",
                "last_msg_url": message.jump_url,
                "notified": False # Tekrar susana kadar bildirim kilidini aç
            })

    async def check_silence_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.now()
            for uid, data in self.targets.items():
                # Geçen süreyi saniye cinsinden hesapla
                elapsed = (now - data["last_time"]).total_seconds()
                
                # Eğer süre dolduysa (1 dk = 60 sn) ve bildirim henüz gitmediyse
                if elapsed >= (BEKLEME_SURESI * 60) and not data["notified"]:
                    self.send_target_webhook(uid, data)
                    data["notified"] = True # Mesaj atana kadar bir daha atmaz
            
            await asyncio.sleep(15) # 15 saniyede bir kontrol eder

    def send_target_webhook(self, user_id, data):
        last_time_str = data["last_time"].strftime("%H:%M:%S")
        
        # Tam istediğin o format
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
        
        try:
            requests.post(WEBHOOK_URL, json=payload)
            print(f"Bildirim tetiklendi: {user_id}")
        except Exception as e:
            print(f"Webhook gönderilemedi: {e}")

client = MySelfBot()
client.run(TOKEN)
