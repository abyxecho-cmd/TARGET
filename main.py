import os
import discord
import asyncio
import requests
from datetime import datetime

# Environment variables (Render üzerinden ayarlanacak)
TOKEN = os.getenv('TOKEN')
TARGET_ID = int(os.getenv('TARGET_ID'))
BEKLEME_SURESI = int(os.getenv('BEKLEME_SURESI'))  # Dakika cinsinden
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

client = discord.Client(intents=discord.Intents.all())

last_message_time = datetime.now()
is_silent = False

def send_webhook_notification():
    data = {
        "content": f"⚠️ **Sessizlik Bildirimi!**\n<@{TARGET_ID}> adlı kullanıcı {BEKLEME_SURESI} dakikadır mesaj atmıyor.",
        "username": "Takip Sistemi"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Webhook gönderilemedi: {e}")

async def monitor_silence():
    global last_message_time, is_silent
    await client.wait_until_ready()
    
    while not client.is_closed():
        # Geçen süreyi hesapla (saniye cinsinden)
        elapsed = (datetime.now() - last_message_time).total_seconds()
        
        if elapsed >= (BEKLEME_SURESI * 60) and not is_silent:
            send_webhook_notification()
            is_silent = True  # Bildirim bir kere gitsin diye kilitliyoruz
            print(f"Hedef {BEKLEME_SURESI} dakikadır sessiz. Bildirim gönderildi.")
        
        await asyncio.sleep(30) # Her 30 saniyede bir kontrol et

@client.event
async def on_ready():
    print(f'Bot aktif: {client.user}')
    client.loop.create_task(monitor_silence())

@client.event
async def on_message(message):
    global last_message_time, is_silent
    
    # Eğer mesajı atan kişi hedef kişiyse süreyi sıfırla
    if message.author.id == TARGET_ID:
        last_message_time = datetime.now()
        if is_silent:
            print("Hedef tekrar aktif oldu.")
            is_silent = False

client.run(TOKEN)
